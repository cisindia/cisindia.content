from zope import schema
from zope.component import getMultiAdapter
from zope.formlib import form
from zope.interface import implements

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.cache import render_cachekey

from Acquisition import aq_inner
from AccessControl import getSecurityManager

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _

from plone.app.vocabularies.catalog import SearchableTextSourceBinder

from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from collective.megaphone.interfaces import IMegaphone


class IMegaphoneCountPortlet(IPortletDataProvider):
    target_megaphone = schema.Choice(
        title=u'Megaphone object',
        description=u'Find the megaphone object for statistic',
        required=True,
        source=SearchableTextSourceBinder(
            {'object_provides' : IMegaphone.__identifier__},
            default_query='path:')
    )

class Assignment(base.Assignment):
    implements(IMegaphoneCountPortlet)

    target_megaphone = None
    title = u'Megaphone count portlet'

    def __init__(self, target_megaphone=None):
        self.target_megaphone = target_megaphone

class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('megaphone.pt')
    render = _template

    available = True


    @memoize
    def megaphone(self):
        obj_path = self.data.target_megaphone
        if not obj_path:
            return None

        if obj_path.startswith('/'):
            obj_path = obj_path[1:]

        portal_state = getMultiAdapter((
            self.context,
            self.request),
            name=u'plone_portal_state'
        )

        portal = portal_state.portal()
        if isinstance(obj_path, unicode):
            obj_path = str(obj_path)

        result = portal.unrestrictedTraverse(obj_path, default=None)
        if result is not None:
            sm = getSecurityManager()
            if not sm.checkPermission('View', result):
                return None

        return result


    def count(self):
        letters = self.megaphone().unrestrictedTraverse('saved-letters',
                default=None)
        if letters is None:
            return 0

        return letters.itemsSaved()

    
class AddForm(base.AddForm):
    form_fields = form.Fields(IMegaphoneCountPortlet)
    form_fields['target_megaphone'].custom_widget = UberSelectionWidget
    label = u'Add Megaphone Count Portlet'
    description = u'This portlet display the email count of megaphone'

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    form_fields = form.Fields(IMegaphoneCountPortlet)
    form_fields['target_megaphone'].custom_widget = UberSelectionWidget
    label = u'Edit Megaphone Count Portlet'
    description = u'This portlet display the email count of megaphone'

