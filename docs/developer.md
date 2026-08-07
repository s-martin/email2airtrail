# Developing

## Releasing a Docker image

To publish a versioned Docker image to GitHub Container Registry, create a Git tag and push it to GitHub:

```bash
git tag v1.0.0
git push origin v1.0.0
```

This triggers the release workflow and publishes images such as:

```bash
ghcr.io/s-martin/email2airtrail:v1.0.0
ghcr.io/s-martin/email2airtrail:latest
```

