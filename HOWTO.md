# How-To Guide

This guide will help you get started with the project.

## Quick Start

### Running the Project Locally

1. Clone the repository:
```bash
git clone https://github.com/username/project.git
cd project
```

2. Open `index.html` in your browser, or use a local server:
```bash
npx serve .
```

### Deploying to GitHub Pages

The project is configured with GitHub Actions for automatic deployment.

1. Push to the `main` branch
2. Go to **Actions** tab in GitHub
3. Watch the deployment workflow run
4. Your site will be available at `https://username.github.io/project/`

### Deploying with Docker

1. Build the Docker image:
```bash
docker build -t project .
```

2. Run the container:
```bash
docker run -p 8080:80 project
```

3. Visit `http://localhost:8080`

## Development

### Project Structure

```
project/
├── index.html      # Main website
├── README.md     # Project readme
├── API.md       # API documentation
├── HOWTO.md     # This guide
└── .github/
    └── workflows/
        └── deploy.yml  # GitHub Pages deployment
```

### Customization

- Edit `index.html` to change the content
- Update SEO meta tags in the `<head>` section
- Modify styles in the `<style>` block

### Adding New Pages

1. Create new HTML files
2. Update links in navigation
3. Commit and push changes

## Troubleshooting

### GitHub Pages Not Deploying

- Ensure the workflow file is in `.github/workflows/`
- Check the Actions tab for errors
- Verify the repository has GitHub Pages enabled in settings

### Docker Issues

- Ensure Docker is running
- Check port 8080 is available
- Try rebuilding the image

## Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [Docker Documentation](https://docs.docker.com/)
- [MDN Web Docs](https://developer.mozilla.org/)