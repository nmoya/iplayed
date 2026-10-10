{ pkgs ? import <nixpkgs> {} }:

let
  zola = pkgs.stdenvNoCC.mkDerivation {
    pname = "zola";
    version = "0.20.0";

    src = pkgs.fetchurl {
      url = "https://github.com/getzola/zola/releases/download/v0.20.0/zola-v0.20.0-x86_64-unknown-linux-gnu.tar.gz";
      sha256 = "021d696g6grvfrswcq9bs4n6b2jpqgjhgqm06mdmp73k7arxazna";
    };

    nativeBuildInputs = [ pkgs.gnutar pkgs.autoPatchelfHook ];
    buildInputs = [ pkgs.stdenv.cc.cc ];

    unpackPhase = "tar -xzf $src";
    installPhase = ''
      install -Dm755 zola $out/bin/zola
    '';
  };
in
pkgs.mkShell {
  packages = with pkgs; [
    python314
    uv
    zola
    git
  ];
}
