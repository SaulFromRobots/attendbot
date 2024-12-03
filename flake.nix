{
	description = "development shell";
	inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

	outputs = { self, nixpkgs }: {
		devShells.x86_64-linux.default = let
			pkgs = nixpkgs.legacyPackages.x86_64-linux;
		in pkgs.mkShell {
			nativeBuildInputs = [ (pkgs.python312.withPackages (p: with p; [
				slack-bolt google-api-python-client google-auth-httplib2 google-auth-oauthlib
			])) ];
		};
	};
}
