# Sources for Kolobok learning module

Store headline, summary, URL, publication timestamp and fetch timestamp first. Do not bypass paywalls, robots.txt, login or technical restrictions. Full article text and media require appropriate permission/licensing.

- Yandex: Yandex Search API in Yandex Cloud. Account and billing required; usage is chargeable. Check pricing and set strict request budgets.
- Google: Custom Search JSON API is closed to new customers. Existing users had a transition deadline of 2027-01-01. Agent Search / Vertex AI Search is a different product and may be paid.
- Bing: legacy Bing Search APIs retired on 2025-08-11. Grounding with Bing Search in Azure AI Agents is a different service.
- Wikipedia: public MediaWiki REST API and Action API. Follow Wikimedia access, caching, attribution and license policies.
- TASS: verified RSS 2.0 feed: https://tass.ru/rss/v2.xml. Follow TASS content citation and reuse rules.
- BBC: Information Syndication API is for authorized syndication partners with contract and API key; not a free public API.
- iXBT: official RSS feeds: https://www.ixbt.com/export/rss.xml ; https://www.ixbt.com/export/articles.rss ; https://www.ixbt.com/export/news.rss . Official export documentation says headlines and links/announcements are provided.
- SecurityLab: correct domain is SecurityLab.ru, not SecurityLab.com. Russian information-security portal covering security news, vulnerabilities, analysis and technology. RSS: https://www.securitylab.ru/_Services/Export/RSS/ and subfeeds /news/, /vulnerabilities/, /analytics/, /software/.

Recommended implementation order: Wikipedia + TASS/iXBT/SecurityLab RSS first; BBC only within permission; Yandex only with cost limits; don't block development waiting for retired Bing or closed-to-new Google API.

Use one adapter per source, with rate limits, caching, exponential backoff and error logs. If a feed only exposes a headline/summary, keep a short digest and link to the original rather than copying whole articles.