import { defineConfig } from '@rsbuild/core';
import { pluginReact } from '@rsbuild/plugin-react';

export default defineConfig({
  plugins: [pluginReact()],
  output: {
    cleanDistPath: true,
    assetPrefix: '/static/',
    distPath: { 
      root: '../static',
      js: 'js',
      css: 'css',
      image: 'img',
    },
  },
});


