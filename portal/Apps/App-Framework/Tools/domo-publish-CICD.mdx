# Domo Publish - GitHub Action

## What is it?

The [Domo Publish Action](https://github.com/marketplace/actions/domo-publish-action) is a GitHub Action that automatically deploys your Domo applications directly from your GitHub repository to your Domo instance. No manual steps, no command-line hasslesjust push your code and let CI/CD handle the rest.

## Why you want to use it

If you're manually running `domo publish` every time you make changes, you're wasting valuable development time. The Domo Publish Action eliminates repetitive deployment tasks by:

- **Automating the entire publish workflow** when code is merged
- **Controlling access to production deployments** without giving every developer publish permissions. Use a dedicated CI/CD service account with properly scoped grants, so only approved code that passes your review process gets deployed
- **Securing your credentials** with GitHub Secrets instead of local tokens
- **Supporting multiple environments** (dev, staging, production)
- **Providing instant feedback** with detailed deployment status in your PR checks

## How it accelerates development

**Traditional workflow:**

1. Make code changes
2. Commit and push
3. Manually run `domo login`
4. Run `domo publish`
5. Wait and monitor
6. Repeat for each environment

**With Domo Publish Action:**

1. Make code changes
2. Push to GitHub
3. Everything else happens automatically

## Quick setup

1. **Get your Domo credentials**: Admin -> Authentication -> Personal Access Tokens
2. **Add to GitHub Secrets**: Store as `DOMO_ACCESS_TOKEN` in your repository
3. **Create workflow file**: Add to `.github/workflows/deploy.yml`
4. **Push and relax**: Your app deploys automatically on merge

```yaml
name: Deploy to Domo
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: DomoApps/domo-publish-action@v1
        with:
          domo-access-token: ${{ secrets.DOMO_ACCESS_TOKEN }}
          build-command: npm run your-build-command
          domo-instance: your-instance.domo.com
          working-directory: ./build
```

**The result?** More time building features, less time managing deployments, credentials, and permissions. Your Domo apps deploy consistently, securely, and automatically with every merge.

## Using with other CI/CD platforms

The Domo Publish Action uses the [Domo CLI](./domo-CLI.md) (`ryuu` npm package) under the hood, which means the same pattern works with any CI/CD platform that supports Node.js. Whether you're using GitLab CI, Jenkins, CircleCI, Azure DevOps, or any other platform, you can adapt this workflow:

**Core pattern:**

```bash
# Install the CLI
npm install -g ryuu

# Authenticate
domo token -i your-instance.domo.com -t $DOMO_ACCESS_TOKEN
domo login -i your-instance.domo.com

# Run Lint, Test, Build, etc.
npm run your-build-command

# Publish your app
cd build && domo publish && cd ..
```

**Example for GitLab CI:**

```yaml
deploy:
  image: node:18
  script:
    - npm install -g ryuu
    - domo token -i your-instance.domo.com -t $DOMO_ACCESS_TOKEN
    - domo login -i your-instance.domo.com
    - domo publish
  only:
    - main
```

The same three-step pattern (install → authenticate → publish) works universally across any CI/CD platform with Node.js support.
