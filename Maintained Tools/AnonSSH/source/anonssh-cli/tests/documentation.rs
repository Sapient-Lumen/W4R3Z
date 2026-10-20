use std::fs;
use std::path::{Path, PathBuf};

#[test]
fn local_markdown_links_resolve() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .expect("workspace root");
    let mut documents = vec![root.join("README.md"), root.join("THIRD_PARTY.md")];
    collect_markdown(&root.join("docs"), &mut documents);

    let mut failures = Vec::new();
    for document in documents {
        check_document(root, &document, &mut failures);
    }

    assert!(
        failures.is_empty(),
        "local Markdown links must resolve:\n{}",
        failures.join("\n")
    );
}

#[test]
fn i2p_curation_does_not_implicitly_record_an_observation() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR"))
        .parent()
        .expect("workspace root");
    let makefile = fs::read_to_string(root.join("Makefile")).expect("read Makefile");
    let target = makefile
        .lines()
        .find(|line| line.starts_with("curate-i2p-bootstrap:"))
        .expect("curate-i2p-bootstrap target");

    assert_eq!(
        target, "curate-i2p-bootstrap: build",
        "curation and dated observation must remain explicit separate operations"
    );
}

fn collect_markdown(directory: &Path, documents: &mut Vec<PathBuf>) {
    let mut entries = fs::read_dir(directory)
        .unwrap_or_else(|error| panic!("read {}: {error}", directory.display()))
        .map(|entry| entry.expect("directory entry").path())
        .collect::<Vec<_>>();
    entries.sort();

    for path in entries {
        if path.is_dir() {
            collect_markdown(&path, documents);
        } else if path.extension().is_some_and(|extension| extension == "md") {
            documents.push(path);
        }
    }
}

fn check_document(root: &Path, document: &Path, failures: &mut Vec<String>) {
    let contents = fs::read_to_string(document)
        .unwrap_or_else(|error| panic!("read {}: {error}", document.display()));
    for (line_index, line) in contents.lines().enumerate() {
        let mut remainder = line;
        while let Some(open) = remainder.find("](") {
            remainder = &remainder[open + 2..];
            let Some(close) = remainder.find(')') else {
                failures.push(format!(
                    "{}:{}: unterminated link destination",
                    relative(root, document),
                    line_index + 1
                ));
                break;
            };
            let destination = remainder[..close].trim().trim_matches(['<', '>']);
            remainder = &remainder[close + 1..];
            if destination.is_empty()
                || destination.starts_with("https://")
                || destination.starts_with("http://")
                || destination.starts_with("mailto:")
            {
                continue;
            }

            let (path, anchor) = destination
                .split_once('#')
                .map_or((destination, None), |(path, anchor)| (path, Some(anchor)));
            let target = if path.is_empty() {
                document.to_path_buf()
            } else {
                document.parent().expect("document parent").join(path)
            };
            if !target.exists() {
                failures.push(format!(
                    "{}:{}: missing {}",
                    relative(root, document),
                    line_index + 1,
                    destination
                ));
                continue;
            }
            if let Some(anchor) = anchor {
                if !anchor.is_empty()
                    && target
                        .extension()
                        .is_some_and(|extension| extension == "md")
                {
                    let target_contents = fs::read_to_string(&target)
                        .unwrap_or_else(|error| panic!("read {}: {error}", target.display()));
                    let found = target_contents
                        .lines()
                        .filter(|candidate| candidate.starts_with('#'))
                        .map(|candidate| candidate.trim_start_matches('#').trim_start())
                        .any(|heading| heading_slug(heading) == anchor);
                    if !found {
                        failures.push(format!(
                            "{}:{}: missing anchor {}",
                            relative(root, document),
                            line_index + 1,
                            destination
                        ));
                    }
                }
            }
        }
    }
}

fn heading_slug(heading: &str) -> String {
    let mut slug = String::new();
    for character in heading.chars().flat_map(char::to_lowercase) {
        if character.is_alphanumeric() || character == '_' || character == '-' {
            slug.push(character);
        } else if character.is_whitespace() {
            slug.push('-');
        }
    }
    slug
}

fn relative(root: &Path, path: &Path) -> String {
    path.strip_prefix(root)
        .unwrap_or(path)
        .display()
        .to_string()
}
