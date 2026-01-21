# Local Development with Domo CLI

## Intro

This comprehensive tutorial will guide you through setting up and optimizing your local development environment using the Domo CLI. You'll learn how to create, develop, debug, and deploy Domo apps efficiently with modern development workflows.

Once published to an instance, your app will be editable as a Pro-Code App. This local development workflow allows you to integrate your preferred AI tooling, IDE, and version control alongside Domo's built-in versioning capabilities.

### What you'll learn

- Setting up a professional local development environment
- Using the Domo Apps CLI to create a new app
- Building your app UI locally with live reload
- Publishing your app to Domo
- Configuring data proxies for consuming live Domo data
- Iterating on your app with full data access

## Prerequisites

Before starting this tutorial, ensure you have:

- **Node.js** installed (version 18 or higher) - This is required for running the Domo CLI and managing dependencies. Use [nvm](https://github.com/nvm-sh/nvm?tab=readme-ov-file#install--update-script) to manage your Node.js version.
- [Domo CLI installed](../Tools/domo-CLI.md#installation)
- A Domo instance with appropriate permissions
- A code editor (VS Code recommended)

## Step 1: Initial Setup and Authentication

### Install and Verify CLI

First, ensure you have the latest version of the Domo CLI:

```bash
# Check current version
domo --version

# Update to latest version (if using npm)
npm update -g ryuu

```

If you haven't installed the Domo CLI yet, you can install it by following the [Setup and Installation Guide](../Tools/domo-CLI.md#installation).

### Authenticate to Your Instance

```bash
# Interactive login
domo login

# Or with specific instance
domo login -i your-instance.domo.com -u your-email@company.com

# Or with a developer access token
domo token -i your-instance.domo.com -t your-developer-access-token*
domo login -i your-instance.domo.com
```

\*Developer Access Tokens (Developer Tokens) are secure API keys assigned to a specific user in your Domo instance. You can get more information and obtain a developer access token by following the [Access Token Guide](https://domo-support.domo.com/s/article/360042934494?language=en_US).

## Step 2: Creating Your Development Project

### Initialize a New App

```bash
# Create a new app with the hello world template
domo init my-awesome-app

# Navigate to your project
cd my-awesome-app
```

### Project Structure

Your new project will have this structure:

```text
my-awesome-app/
├── manifest.json        # App configuration
├── index.html           # Main HTML file
├── app.js               # Main JavaScript
├── app.css              # Styles
├── domo.js              # Domo SDK
└── assets/              # Static assets
```

### Understanding the Manifest

The `manifest.json` is crucial for local development:

```json
{
  "name": "My Awesome App",
  "version": "1.0.0",
  "size": {
    "width": 1,
    "height": 1
  },
  "fullpage": false,
  "mapping": [
    {
      "dataSetId": "your-dataset-id",
      "alias": "myData",
      "fields": [
        {
          "columnName": "sales",
          "alias": "revenue"
        }
      ]
    }
  ],
  "collections": [
    {
      "name": "CommentsTable",
      "schema": {
        "columns": [
          { "name": "user", "type": "STRING" },
          { "name": "comment", "type": "STRING" }
        ]
      },
      "syncEnabled": true,
      "defaultPermission": ["READ", "WRITE", "READ_CONTENT", "CREATE_CONTENT"]
    },
    {
      "name": "Users"
    }
  ],
  "id": "your-app-design-id",
  "proxyId": "your-remote-domo-card-id"
}
```

**Key manifest properties for local development:**

- `id`: The ID of your app design in Domo
  - This is automatically added to your manifest when you publish your app design
  - This is used to link your app design to the published app design for future publishing
  - This is used to identify your app design in the Domo API
- `proxyId`: Enables API proxying for live data
- `mapping`: Defines data connections
- `size`: Sets app dimensions within Domo

See our guide on [The Manifest File](./manifest.md) for more information.

### Adding a Thumbnail

📸 **Required**: You must add a thumbnail image to your app design before you can create cards from it.

**How to add a thumbnail:**

1. **Create or find an image** (PNG) - it must be named `thumbnail.png` and it must be 300x300 pixels
2. **Add it to your project folder** (e.g., `thumbnail.png`)

**Need a quick thumbnail?** You can use this [sample thumbnail](../../../../assets/images/thumbnail-procode.png) as a starting point.

## Step 3: Initial Local Development

### Development Server Features

The `domo dev` command provides:

- **Live Reload**: Browser automatically refreshes when files change
- **App Sizing**: Renders in a frame matching your manifest dimensions
- **Local Testing**: Build and test your UI before publishing

### Development Workflow

```bash
# 1. Start development server
domo dev

# 2. Open browser to http://localhost:3000
# 3. Make changes to your code
# 4. See changes instantly in browser
```

**Note**: At this stage, you can build your UI and basic functionality, but data queries won't work yet. You'll need to publish your app first to get a proxy ID for data access.

## Step 4: Publishing Your App Design

### Publishing Your App

```bash
# Publish to Domo
domo publish

```

### Important: Version Management

⚠️ **Critical**: When you publish your app, Domo will update the existing version if it already exists. If you want to keep previous versions, you **_must_** increment the version number in your `manifest.json` **_(not the package.json)_** before publishing.

```json
{
  "version": "1.0.1",
  "name": "My Awesome App"
}
```

**What happens:**

- If you publish with the same version number → **Previous version is overwritten**
- If you increment the version number → **Previous version is preserved for rolling back**

## Step 5: Configuring Data Access

Now that your app is published, you can set up data access for local development.

### Getting a Proxy ID

To enable data queries during local development, you need to configure a proxy card:

1. **Create a card** from your published app design in Domo
2. **Wire up your datasets** to the card
3. **Copy the card ID** from the URL (the string after `/kpis/details/`)
4. **Add it to your manifest** as the `proxyId` field

```json
{
  "id": "your-app-design-id",
  "proxyId": "your-card-id-here"
}
```

### How Data Proxying Works

To keep things secure, local queries to Domo are proxied through a card in your Domo instance. Using the manifest's Design ID and Proxy ID, requests are passed to the card, and the card's response is returned to the local development server.

This approach uses indirect access to your Domo instance's API, which is a security best practice and is required for using AppDB, Workflows, Code Engine, and other Domo services.

See our guide on [The Manifest File](./manifest.md#getting-a-proxyid-advanced) for more information.

## Step 6: Full Development Workflow

With your proxy ID configured, you now have the complete development workflow:

```bash
# 1. Start development server
domo dev

# 2. Open browser to http://localhost:3000
# 3. Make changes to your code
# 4. See changes instantly in browser
# 5. Test with real Domo data
# 6. Publish updates with domo publish
```

### Testing Checklist

Verify your app works correctly:

- [ ] App loads without errors
- [ ] Data queries return expected results
- [ ] UI looks good and functions properly
- [ ] All features work as intended

## Conclusion

Congratulations! You've learned the essential workflow for local development with the Domo CLI:

✅ **Setup**: Install Node.js and Domo CLI

✅ **Login**: Authenticate to your Domo instance

✅ **Create**: Initialize a new app with `domo init`

✅ **Build**: Develop your UI locally with `domo dev`

✅ **Publish**: Deploy your app with `domo publish`

✅ **Configure**: Set up data access with a proxy ID

✅ **Iterate**: Continue developing with full data access

### Next Steps

- Explore the [Domo Apps CLI documentation](../Tools/domo-CLI.md) for more advanced features
- Check out other [tutorials](./Overview.md) for specific app types
- Join the [Domo Developer Community](https://developer.domo.com/community)

---

**Happy coding!** 🚀
