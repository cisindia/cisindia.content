from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.EasyNewsletter.portlets.subscriber import Renderer as BaseRenderer


class Renderer(BaseRenderer):
    render = ViewPageTemplateFile('custom.pt')
