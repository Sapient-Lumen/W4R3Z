# Source lanes and rev0003 fetch instructions

        ## Why these lanes exist

        The cube must not judge findings only against old 3.3.10 source. Current supported and future branches may already fix, partially fix, refactor, or publicly overlap a row.

        ## Current rev0002 source-lane status

        | lane | target | status_in_rev0002 | why |
| --- | --- | --- | --- |
| stable-release-baseline | tag 3.3.10 | carried from prior uploaded cube where available; not live-fetched here | current stable and supported release baseline |
| supported-release-candidate | branch 3.3.x / 3.3.11 RC lane | not fetched; fetch script prepared for rev0003 | candidate fixes may already exist in 3.3.x and must be checked before promotion |
| future-default-development | master / 3.4.0.dev1 lane | not fetched; fetch script prepared for rev0003 | future/default fixes may make items known/upstream-adjacent or change severity |
| release-metadata | releases, milestones, open issues, open PRs | web-observed notes recorded; fetch script prepared for API snapshots | public overlap and near-release changes are high-risk for false novelty |
| pypi-release-artifacts | nicotine-plus==3.3.10 sdist/wheel | carried from prior cube where available; fetch script also downloads fresh copies | compare GitHub tag vs packaged release artifacts |


        ## Run this locally before rev0003

        From any clean working directory on a machine with GitHub access:

        ```bash
        bash tools/fetch_nicotine_upstream_sources_for_rev0003.sh
        ```

        Or, if you copy just the script out of the cube:

        ```bash
        chmod +x fetch_nicotine_upstream_sources_for_rev0003.sh
        ./fetch_nicotine_upstream_sources_for_rev0003.sh
        ```

        The script creates a directory and then packages it as `.zip` if `zip` is available, otherwise `.tar.gz`. Upload that archive for rev0003. In rev0003 I will unpack it under:

        ```text
        sources/upstream-current-and-future/
        ```

        ## Expected upload contents

        ```text
        source-trees/github-tag-3.3.10/
        source-trees/github-branch-3.3.x/
        source-trees/github-branch-master/
        archives/
        pypi/
        metadata/
        logs/
        SHA256SUMS
        README-FOR-REV0003.md
        ```

        ## Container limitation recorded

        The local container command `git ls-remote --heads --tags https://github.com/nicotine-plus/nicotine-plus.git` failed with DNS resolution. This is recorded in `evidence/live-github-fetch-attempt.txt`.
