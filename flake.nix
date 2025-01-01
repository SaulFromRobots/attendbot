{
	description = "development shell";
	inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

	outputs = { self, nixpkgs }: let
		pkgs = nixpkgs.legacyPackages.x86_64-linux;
	in {
		devShells.x86_64-linux.default = pkgs.mkShell {
			nativeBuildInputs = [ (pkgs.python312.withPackages (p: with p; [ slack-bolt google-api-python-client google-auth-httplib2 google-auth-oauthlib ])) ];
		};
		packages.x86_64-linux = rec {
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
				config.Cmd = [ (default+"/bin/attendbot") ];
			};
		};
	};
}
