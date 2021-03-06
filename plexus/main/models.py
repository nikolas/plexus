from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=256)
    details = models.TextField(blank=True, default=u"")

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/location/%d/" % self.id


class OSFamily(models.Model):
    name = models.CharField(max_length=256)

    class Meta:
        ordering = ['name', ]

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/os/%d/" % self.id


class OperatingSystem(models.Model):
    family = models.ForeignKey(OSFamily)
    version = models.CharField(max_length=256)

    class Meta:
        ordering = ['version', ]

    def __unicode__(self):
        return unicode(self.family) + " " + self.version

    def get_absolute_url(self):
        return "/os/%d/%d/" % (self.family.id, self.id)


class Server(models.Model):
    name = models.CharField(max_length=256)
    primary_function = models.TextField(blank=True, default=u"")
    virtual = models.BooleanField()
    location = models.ForeignKey(Location, null=True, default="")
    operating_system = models.ForeignKey(OperatingSystem)
    memory = models.CharField(max_length=256, blank=True)
    disk = models.CharField(max_length=256, blank=True)
    swap = models.CharField(max_length=256, blank=True)
    notes = models.TextField(blank=True, default=u"")
    deprecated = models.BooleanField(default=False)
    graphite_name = models.CharField(max_length=256, default=u"", blank=True)
    sentry_name = models.CharField(max_length=256, default=u"", blank=True)
    munin_name = models.CharField(max_length=256, default=u"", blank=True)

    class Meta:
        ordering = ['name', ]

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/server/%d/" % self.id

    def add_contacts(self, contacts):
        for c in contacts:
            contact, created = Contact.objects.get_or_create(name=c)
            ServerContact.objects.create(server=self,
                                         contact=contact)

    def set_contacts(self, contacts):
        self.servercontact_set.all().delete()
        self.add_contacts(contacts)

    def ipaddress_default(self, ipaddress_id):
        if ipaddress_id:
            return IPAddress.objects.get(id=ipaddress_id)
        return self.ipaddress_set.all()[0]

    def potential_dom0s(self):
        return Server.objects.filter(virtual=False).exclude(id=self.id)


class IPAddress(models.Model):
    ipv4 = models.CharField(max_length=256)
    mac_addr = models.CharField(max_length=256)
    server = models.ForeignKey(Server)

    def __unicode__(self):
        return self.ipv4


class VMLocation(models.Model):
    dom_u = models.ForeignKey(Server, related_name='dom_u')
    dom_0 = models.ForeignKey(Server, related_name='dom_0')

    def __unicode__(self):
        return unicode(self.dom_u)


class Contact(models.Model):
    name = models.CharField(max_length=256)
    email = models.CharField(max_length=256, default="")
    phone = models.CharField(max_length=256, default="")

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return "/contact/%d/" % self.id


class Alias(models.Model):
    hostname = models.CharField(max_length=256)
    ip_address = models.ForeignKey(IPAddress, null=True)
    status = models.CharField(max_length=256, default=u"active")
    description = models.TextField(blank=True, default=u"")
    administrative_info = models.TextField(
        blank=True,
        default=u"",
        help_text=("Required if not a .ccnmtl.columbia.edu hostname."
                   "Please use this field for information about "
                   "where the domain is registered, what account "
                   "it's set up with (don't enter passwords here though) "
                   "and who handles payments, DNS changes, etc."))

    class Meta:
        ordering = ['hostname', ]

    def __unicode__(self):
        return self.hostname

    def status_css_class(self):
        if self.status == 'pending':
            return "warning"
        if self.status == 'deprecated':
            return "error"
        return ""

    def can_request_dns_change(self):
        """ it's not safe for Plexus to try to request DNS changes
        outside our subdomain"""
        return str(self.hostname).endswith(".ccnmtl.columbia.edu")

    def dns_change_request_email_subject(self):
        return "DNS Alias Change Request: " + self.hostname

    def dns_request_email_subject(self):
        return "DNS Alias Request: " + self.hostname

    def dns_request_email_body(self, requester):
        return """
Please add the following alias:

      %s

It should resolve to %s (%s)

Thanks,
%s
""" % (self.hostname, self.ip_address.server.name,
       self.ip_address.ipv4, requester)

    def dns_change_request_email_body(self, current_server, current_ip_address,
                                      requester):
        return """
Please change the following alias:

    %s

Which currently is an alias for %s (%s).

It should be changed to instead point to %s (%s).

Thanks,
%s
""" % (self.hostname, current_server.name, current_ip_address.ipv4,
       self.ip_address.server.name, self.ip_address.ipv4,
       requester)

    def add_contacts(self, contacts):
        for c in contacts:
            contact, created = Contact.objects.get_or_create(name=c)
            AliasContact.objects.create(alias=self, contact=contact)

    def set_contacts(self, contacts):
        self.aliascontact_set.all().delete()
        self.add_contacts(contacts)

    def get_absolute_url(self):
        return "/alias/%d/" % self.id


class AliasContact(models.Model):
    alias = models.ForeignKey(Alias)
    contact = models.ForeignKey(Contact)

    class Meta:
        order_with_respect_to = 'alias'

    def __unicode__(self):
        return unicode(self.alias) + ": " + unicode(self.contact)


class Technology(models.Model):
    name = models.CharField(max_length=256)

    def __unicode__(self):
        return self.name


class Application(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True, default=u"")
    technology = models.ForeignKey(Technology, null=True)
    graphite_name = models.CharField(max_length=256, default=u"", blank=True)
    sentry_name = models.CharField(max_length=256, default=u"", blank=True)
    pmt_id = models.IntegerField(default=0)
    # rolf
    # code repos
    # renewals
    # google analytics

    class Meta:
        ordering = ['name', ]

    def __unicode__(self):
        return self.name

    def pmt_feed_url(self):
        return ("http://pmt.ccnmtl.columbia.edu/project_feed.pl?pid=%d"
                % self.pmt_id)

    def add_contacts(self, contacts):
        for c in contacts:
            contact, created = Contact.objects.get_or_create(name=c)
            ApplicationContact.objects.create(application=self,
                                              contact=contact)

    def set_contacts(self, contacts):
        self.applicationcontact_set.all().delete()
        self.add_contacts(contacts)

    def get_absolute_url(self):
        return "/application/%d/" % self.id


class ApplicationAlias(models.Model):
    application = models.ForeignKey(Application)
    alias = models.ForeignKey(Alias)

    def __unicode__(self):
        return unicode(self.application) + " -> " + unicode(self.alias)


class ApplicationContact(models.Model):
    application = models.ForeignKey(Application)
    contact = models.ForeignKey(Contact)

    class Meta:
        order_with_respect_to = 'application'

    def __unicode__(self):
        return unicode(self.application) + ": " + unicode(self.contact)


class ServerContact(models.Model):
    server = models.ForeignKey(Server)
    contact = models.ForeignKey(Contact)

    class Meta:
        order_with_respect_to = 'server'

    def __unicode__(self):
        return unicode(self.server) + ": " + unicode(self.contact)
