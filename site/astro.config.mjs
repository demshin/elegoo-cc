import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';
import manifest from './content-manifest.json' with { type: 'json' };

const googleAnalyticsId = process.env.PUBLIC_GOOGLE_ANALYTICS_ID?.trim();
if (googleAnalyticsId && !/^G-[A-Z0-9]+$/.test(googleAnalyticsId)) {
  throw new Error('PUBLIC_GOOGLE_ANALYTICS_ID must be a GA4 measurement ID (G-...).');
}

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
      head: googleAnalyticsId ? [
        {
          tag: 'script',
          attrs: { async: true, src: `https://www.googletagmanager.com/gtag/js?id=${googleAnalyticsId}` },
        },
        {
          tag: 'script',
          content: `window.dataLayer = window.dataLayer || [];
function gtag(){dataLayer.push(arguments);}
gtag('js', new Date());
gtag('config', '${googleAnalyticsId}');`,
        },
      ] : [],
      customCss: ['./src/styles/custom.css'],
      components: { Header: './src/components/Header.astro' },
      sidebar: [
        { label: 'Начать здесь', items: [{ slug: '' }, { slug: 'start/beginners' }, { slug: 'start/advanced' }, { slug: 'start/models' }] },
        ...manifest.groups.map(group => ({
          label: group.label,
          collapsed: true,
          items: [
            { slug: group.route, label: 'Все статьи темы' },
            ...manifest.pages.filter(page => page.group === group.id).map(page => ({ slug: page.route })),
          ],
        })),
        { label: 'Основания и метод', collapsed: true, items: manifest.pages.filter(page => page.group === 'sources').map(page => ({ slug: page.route })) },
      ],
      tableOfContents: { minHeadingLevel: 2, maxHeadingLevel: 3 },
      social: [{ icon: 'telegram', label: 'Сообщество в Telegram', href: 'https://t.me/CentauriCarbon' }],
    }),
  ],
});
