#!/usr/bin/env bash

rm -f Cargo.toml Cargo.lock
curl -OL "https://static.rust-lang.org/dist/rust-1.66.0-x86_64-unknown-linux-gnu.tar.gz"
tar xzvf rust-1.66.0-x86_64-unknown-linux-gnu.tar.gz
rm rust-1.66.0-x86_64-unknown-linux-gnu.tar.gz
./rust-1.66.0-x86_64-unknown-linux-gnu/install.sh
cargo init --name piston
cargo add anyhow base64 futures futures-util hex itertools log rand serde -F serde/derive serde_json tokio -F tokio/full
cargo build
rm ./target/debug/deps/piston*