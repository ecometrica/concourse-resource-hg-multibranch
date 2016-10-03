# Concourse Mercurial Multibranch.

This resource can be used to build multiple branches in a mercurial repo. 
It is heavily inspired by [starkandwayne/git-multibranch-resource](https://github.com/starkandwayne/git-multibranch-resource)

Very early stages. Currently no filtering what so ever. Just builds
all (non-closed) branches. No pushing.

### TODO:
- Implement features of the git-multibranch resource. Things like
  regexp filtering, file filtering, etc.
- Tests

### Source Configuration

    uri: Required. The location of the repository.
    private_key: Optional. Private key to use when pulling/pushing.
    
