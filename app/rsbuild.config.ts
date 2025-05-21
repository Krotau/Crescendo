import { defineConfig } from '@rsbuild/core';
import { pluginReact } from '@rsbuild/plugin-react';

export default defineConfig({
  plugins: [pluginReact()],
  output: {
    distPath: {
      root: '../',
      js: 'gui/js',
      html: 'gui',
      css: 'static',
      image: 'static',
    },
  },
});


