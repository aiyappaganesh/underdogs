# Python bindings to oDesk API
# python-odesk version 0.5
# (C) 2010-2014 oDesk

from odesk.namespaces import Namespace
from odesk.utils import assert_parameter, ApiValueError


class Offers(Namespace):
    """
    Offers API version 1
    """
    api_url = 'offers/'
    version = 1

    def list_client_offers(self, company_id=None, team__reference=None,
                           job__reference=None, status=None,
                           page_offset=None, page_size=None):
        """
        List client offers.

        *Parameters:*
          :company_id:       (optional) The client's company reference ID.
                             Example: ``34567``. Get it using 'List companies'
                             API call. If ``company_id`` is not specified,
                             the API will infer it from job's data relying on
                             the provided ``job__reference`` parameter. Either
                             ``company_id`` or ``job__reference`` parameter must be specified.

          :team__reference:  (optional) The client's team reference ID. Example: ``34567``. Get it using
                             'List teams' API call. Please note, that if ``team__reference``
                             is not specified, the API will infer it from job's data relying on the provided.

          :job__reference:   (optional) The job reference ID. Get it using 'List jobs' API call.

          :status:           (optional) The current status of the Offer. By default only offers in status `new` are returned.
                             Valid values: ``accepted``, ``new``, ``declined``,
                             ``expired``, ``withdrawn``, ``cancelled``, ``changed``.

          :page_offset:      (optional) Number of entries to skip

          :page_size:        (optional: default 20) Page size in number
                             of entries

        """
        data = {}

        if company_id:
            data['company_id'] = company_id

        if team__reference:
            data['team__reference'] = team__reference

        if job__reference:
            data['job__reference'] = job__reference

        if status:
            data['status'] = status

        if page_offset:
            data['page'] = '{0};{1}'.format(page_offset, page_size)

        url = 'clients/offers'
        return self.get(url, data)

    def send_client_offer(self, title, job_type, charge_rate,
                          message_to_contractor, team__reference=None,
                          client_team_ref=None, contractor_username=None,
                          contractor_reference=None, contractor_key=None,
                          contractor_org=None, context=None,
                          charge_upfront_percent=None, weekly_limit=None,
                          weekly_stipend=None, expires_on=None,
                          close_on_accept=None):
        """
        Send client offer to the freelancer.

        *Parameters:*
          :title:                    The title of the offer/contract.

          :job_type:                 The type of the job. Valid values: ``hourly``, ``fixed-price``.

          :charge_rate:              The budget amount for fixed-price jobs or the hourly charge rate for hourly jobs.

          :message_to_contractor:    Instructions and other job details for the freelancer.

          :team__reference:          The client's team reference ID. Example: ``34567``. Use 'List teams' API call to get it.

          :client_team_ref:          The client's team reference. Example: ``mytestcompany:myteam``. Use 'List teams' API call to get it.

          :contractor_username:      The freelancer's username. Example: ``contractoruid``.
                                     It can be ignored if ``contractor_reference`` or ``contractor_key`` parameter is set.

          :contractor_reference:     The freelancer's reference ID. It will be ignored if ``contractor_username`` or ``contractor_key``
                                     is specified. Example: ``1234``. You can use 'Search freelancers' API call to get the freelancer's reference ID.

          :contractor_key:           The unique profile key, used if ``contractor_username`` is absent. Example: ``~~677961dcd7f65c01``.

          :contractor_org:           The freelancer's team reference, required for sending offers to agency freelancers.

          :context:                  Additional data about the offer. Valid array keys are: ``previous_offer_ref``,
                                     ``job_posting_ref``, ``job_application_ref``, ``contract_ref``.
                                     Example: ``context[job_posting_ref] = {{ opening_id }} & context[job_application_ref] = {{ application_id }}``
                                     where ``job_posting_ref`` is a job key, for example ``~01c8e0xxxxxxxx05255``.

          :charge_upfront_percent:   The percentage of the budget amount that the freelancer is paid on acceptance of the offer
                                     (for fixed price jobs only).

          :weekly_limit:             The maximum number of hours per week the freelancer can bill for.

          :weekly_stipend:           An additional payment to be issued to the freelancer each week.

          :expires_on:               Time when the offer expires. This should be a UNIX UTC timestamp. For example: ``1400785324``.

          :close_on_accept:          If the value is ``1``, it automatically closes the related job post if this offer is accepted.
                                     The default value is ``1``. Valid values: ``0``, ``1``.

        """
        data = {}

        data['title'] = title
        data['job_type'] = job_type
        data['charge_rate'] = charge_rate
        data['message_to_contractor'] = message_to_contractor

        if team__reference:
            data['team__reference'] = team__reference

        if client_team_ref:
            data['client_team_ref'] = client_team_ref

        if contractor_username:
            data['contractor_username'] = contractor_username

        if contractor_reference:
            data['contractor_reference'] = contractor_reference

        if contractor_key:
            data['contractor_key'] = contractor_key

        if charge_upfront_percent:
            data['charge_upfront_percent'] = charge_upfront_percent

        if context:
            data['context'] = context

        if weekly_limit:
            data['weekly_limit'] = weekly_limit

        if weekly_stipend:
            data['weekly_stipend'] = weekly_stipend

        if expires_on:
            data['expires_on'] = expires_on

        if close_on_accept:
            data['close_on_accept'] = close_on_accept

        url = 'clients/offers'
        return self.post(url, data)

    def get_client_offer(self, offer_id, company_id=None, job__reference=None):
        """
        Get offer as client.

        *Parameters:*
          :offer_id:         Offer reference ID.

          :company_id:       (optional) The client's company reference ID.
                             Example: ``34567``. Get it using 'List companies'
                             API call. If ``company_id`` is not specified,
                             the API will infer it from job's data relying on
                             the provided ``job__reference`` parameter. Either
                             ``company_id`` or ``job__reference`` parameter must be specified.

          :job__reference:   (optional) The job reference ID. Get it using 'List jobs' API call.

        """
        data = {}

        data['offer_id'] = offer_id

        if company_id:
            data['company_id'] = company_id

        if job__reference:
            data['job__reference'] = job__reference

        url = 'clients/offers/{0}'.format(offer_id)
        return self.get(url, data)

    def list_freelancer_offers(self, status=None,
                               page_offset=None, page_size=None):
        """
        List freelancer's offers.

        *Parameters:*
          :status:           (optional) The current status of the Offer. By default only offers in status `new` are returned.
                             Valid values: ``accepted``, ``new``, ``declined``,
                             ``expired``, ``withdrawn``, ``cancelled``, ``changed``.

          :page_offset:      (optional) Number of entries to skip

          :page_size:        (optional: default 20) Page size in number
                             of entries

        """
        data = {}

        if status:
            data['status'] = status

        if page_offset:
            data['page'] = '{0};{1}'.format(page_offset, page_size)

        url = 'contractors/offers'
        return self.get(url, data)

    def get_freelancer_offer(self, offer_id):
        """
        Get specific offer as freelancer.

        *Parameters:*
          :offer_id:         Offer reference ID.

        """
        data = {}

        data['offer_id'] = offer_id

        url = 'contractors/offers/{0}'.format(offer_id)
        return self.get(url, data)
