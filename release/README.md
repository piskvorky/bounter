# Release Procedure

1. Bump the version in `bounter/__init__.py`
2. Bump the version in `setup.py`
3. Update CHANGELOG.md with PRs merged since the last release
4. Commit your changes
5. Run release/release.sh 1.2.3 where 1.2.3 is the version you're releasing

## Updating the Change Log

Eyeball https://github.com/RaRe-Technologies/bounter/pulls?q=is%3Apr+is%3Aclosed for PRs closed since the last release, then run:

    $ bash release/summarize_pr.sh 53 41
    * Add 64bit Min Sketch (__[@jponf](https://github.com/jponf)__, [#53](https://github.com/RaRe-Technologies/bounter/pull/53))
    * Issue33: pickle mem leak (__[@isamaru](https://github.com/isamaru)__, [#41](https://github.com/RaRe-Technologies/bounter/pull/41))

You can now copy-paste these summaries into CHANGELOG.md
