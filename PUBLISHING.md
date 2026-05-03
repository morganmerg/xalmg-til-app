# Publishing Checklist

Recommended repository name: `xalmg-til-app`

Before pushing:

```bash
npm install
npx tsc --noEmit
npx expo-doctor
```

Do not commit:

- `node_modules/`
- `.expo/`
- `scripts/_merge_src/`
- local `.env` files
- local source packs such as Lingvo archives or extracted audio directories

Suggested first commit:

```bash
git init
git add .
git commit -m "Initial public mobile learning app prototype"
git branch -M main
git remote add origin https://github.com/<user>/xalmg-til-app.git
git push -u origin main
```

GitHub profile pin text:

> Offline Expo/React Native app for learning Kalmyk with bundled SQLite/FTS dictionary, local progress tracking, and verified Expo health checks.
