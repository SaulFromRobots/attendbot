{
	description = "development shell";
	inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

	outputs = { self, nixpkgs }: let
		pkgs = nixpkgs.legacyPackages.x86_64-linux;
		deps = pkgs.python312.withPackages (p: with p; [
			slack-bolt google-api-python-client google-auth-httplib2 google-auth-oauthlib
		]);
		in {
		devShells.x86_64-linux.default = pkgs.mkShell {
			nativeBuildInputs = [ deps ];
		};
		packages.x86_64-linux = {
			default = with pkgs.python312Packages; buildPythonPackage {
				pname = "attendbot";
				version = "main";
				dependencies = [ slack-bolt google-api-python-client google-auth-httplib2 google-auth-oauthlib ];
				format = "pyproject";
				build-system = [ setuptools ];
				src = ./.;
			};
			image = pkgs.dockerTools.buildImage {
				name = "attendbot";
				tag = "latest";
				copyToRoot = [ ./. ];
				config.Cmd = [ (self.default+"/bin/attendbot") ];
			};
		};
	};
}
