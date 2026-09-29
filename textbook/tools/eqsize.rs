use std::io::{self, BufRead};
// stdin: "<baseUnit>\t<script>" per line -> stdout "<w>\t<h>"
fn main() {
    let stdin = io::stdin();
    for line in stdin.lock().lines() {
        let line = line.unwrap();
        let mut it = line.splitn(2, '\t');
        let base: u32 = it.next().unwrap().parse().unwrap();
        let script = it.next().unwrap_or("");
        let (w, h) = rhwp::renderer::equation::intrinsic_size_hwp(script, base);
        println!("{}\t{}", w, h);
    }
}
