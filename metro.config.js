// Extend asset extensions so expo-sqlite can bundle .db files
const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// SQLite database and raw audio
config.resolver.assetExts.push('db', 'wav');

module.exports = config;
