"""Helper for mkdocs to prepare docs-Directory."""

from pathlib import Path

import git
import mkdocs_gen_files


def copy_files():
    _copy = {
        "index.md": "README.md",
        "LICENSE.md": "LICENSE.md",
        "CHANGELOG.md": "CHANGELOG.md",
    }

    for target_path, source_path in _copy.items():
        source = Path(source_path)
        if source.is_file():
            with mkdocs_gen_files.open(target_path, "w") as target:
                target.write(source.open().read())


def generate_api_reference():
    nav = mkdocs_gen_files.Nav()

    repo = git.Repo(".", search_parent_directories=True)
    for path in sorted(
        Path(blob.path)
        for blob in repo.commit()
        .tree["src"]
        .traverse(predicate=lambda i, d: i.path.endswith(".py"))
    ):
        module_path = path.relative_to("src").with_suffix("")
        doc_path = module_path.with_suffix(".md")
        full_doc_path = Path("api", doc_path)

        parts = list(module_path.parts)

        if parts[-1] == "__init__":
            parts = parts[:-1]
            doc_path = doc_path.with_name("index.md")
            full_doc_path = full_doc_path.with_name("index.md")
        elif parts[-1] == "__main__":
            continue

        nav[parts] = doc_path.as_posix()

        with mkdocs_gen_files.open(full_doc_path, "w") as fd:
            identifier = ".".join(parts)
            print("::: " + identifier, file=fd)

        mkdocs_gen_files.set_edit_path(full_doc_path, path)

    with mkdocs_gen_files.open("api/SUMMARY.md", "w") as nav_file:
        nav_file.writelines(nav.build_literate_nav())


copy_files()
generate_api_reference()
