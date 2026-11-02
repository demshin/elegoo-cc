import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import manifest from './content-manifest.json' with { type: 'json' };

export default defineConfig({
  site: process.env.SITE_URL || 'http://localhost:4321',
  base: process.env.SITE_BASE || '/',
  trailingSlash: 'always',
  integrations: [
    starlight({
      title: 'Elegoo Centauri Carbon',
      description: 'FAQ сообщества Elegoo Centauri Carbon: проверяемые решения для FDM-печати.',
      defaultLocale: 'root',
      locales: { root: { label: 'Русский', lang: 'ru' } },
      favicon: '/favicon.svg',
      customCss: ['./src/styles/custom.css'],
      components: { Header: './src/components/Header.astro' },
      sidebar: [
        { label: 'Начать здесь', items: [{ slug: '' }, { slug: 'start/beginners' }, { slug: 'start/advanced' }, { slug: 'start/models' }] },
        ...manifest.groups.map(group => ({
          label: group.label,
          collapsed: true,
          items: manifest.pages.filter(page => page.group === group.id).map(page => ({ slug: page.route })),
        })),
        { label: 'Основания и метод', collapsed: true, items: manifest.pages.filter(page => page.group === 'sources').map(page => ({ slug: page.route })) },
      ],
      tableOfContents: { minHeadingLevel: 2, maxHeadingLevel: 3 },
      social: [{ icon: 'telegram', label: 'Сообщество в Telegram', href: 'https://t.me/CentauriCarbon' }],
    }),
  ],
});
