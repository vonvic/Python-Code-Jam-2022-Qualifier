import typing
from dataclasses import dataclass

@dataclass(frozen=True)
class Request:
    scope: typing.Mapping[str, typing.Any]

    receive: typing.Callable[[], typing.Awaitable[object]]
    send: typing.Callable[[object], typing.Awaitable[None]]


class RestaurantManager:
    def __init__(self):
        """Instantiate the restaurant manager.

        This is called at the start of each day before any staff get on
        duty or any orders come in. You should do any setup necessary
        to get the system working before the day starts here; we have
        already defined a staff dictionary.
        """
        self.staff = {}

    async def __call__(self, request: Request):
        """Handle a request received.

        This is called for each request received by your application.
        In here is where most of the code for your system should go.

        :param request: request object
            Request object containing information about the sent
            request to your application.
        """
        match request.scope['type']:
            case 'staff.onduty':
                self.staff[request.scope['id']] = request
            case 'staff.offduty':
                del self.staff[request.scope['id']]
            case 'order':
                found = self._get_staff_member(request.scope['speciality'])

                full_order = await request.receive()
                await found.send(full_order)

                result = await found.receive()
                await request.send(result)

    def _get_staff_member(self, order_specialty: str):
        '''Returns the first staff member that specializes in the order
        specialty.'''
        for request in self.staff.values():
            if order_specialty in request.scope['speciality']: return request