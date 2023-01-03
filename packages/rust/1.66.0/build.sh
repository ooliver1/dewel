#!/usr/bin/env bash

curl -OL "https://static.rust-lang.org/dist/rust-1.66.0-x86_64-unknown-linux-gnu.tar.gz"
tar xzvf rust-1.66.0-x86_64-unknown-linux-gnu.tar.gz
rm rust-1.66.0-x86_64-unknown-linux-gnu.tar.gz
rm -r rust-1.66.0-x86_64-unknown-linux-gnu/rust-docs
./rust-1.66.0-x86_64-unknown-linux-gnu/cargo/bin/cargo init --name piston
./rust-1.66.0-x86_64-unknown-linux-gnu/cargo/bin/cargo add anyhow futures itertools log rand serde serde_json tokio
rm ./target/release/deps/piston*