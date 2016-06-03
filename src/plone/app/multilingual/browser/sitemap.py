from plone.app.layout.sitemap.sitemap import SiteMapView


class PAM1xSiteMapView(SiteMapView):
    """Overrides SiteMapView with patch for p.a.multilingual 1.x
    """

    def extra_search_parameters(self):
        """Work around PAM 1.x's catalog patch."""
        # see https://github.com/plone/plone.app.multilingual/blob/1.x/src/plone/app/multilingual/catalog.py
        return {'Language': 'all'}
