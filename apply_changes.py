import re
import os

def update_file(path, pattern, replacement, flags=0, append=None):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if pattern:
        content = re.sub(pattern, replacement, content, flags=flags)
    if append:
        content += '\n' + append
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# 1. Update frontend/lib/api.ts
api_ts_path = 'c:/Users/EX BOOK/Desktop/hotel/frontend/lib/api.ts'
with open(api_ts_path, 'r', encoding='utf-8') as f:
    api_content = f.read()

# Replace addServiceToBooking
api_content = re.sub(
    r'export async function addServiceToBooking.*?\}',
    '''export async function addServiceToBooking(bookingId: number, serviceName: string, serviceTotal: number, serviceDates: number = 1): Promise<{ success: boolean; message: string }> {
  try {
    await request(`/api/v1/bookings/${bookingId}/services`, { 
      method: 'POST',
      body: JSON.stringify({ service_name: serviceName, service_total: serviceTotal, service_dates: serviceDates })
    });
    return { success: true, message: 'Service added successfully' };
  } catch (e: any) {
    return { success: false, message: e.message ?? 'Failed to add service' };
  }
}''',
    api_content,
    flags=re.DOTALL
)

# Replace extendStay (if it's stubbed)
api_content = re.sub(
    r'export async function extendStay.*?\}',
    '''export async function extendStay(bookingId: number, newCheckOutDate: string): Promise<{ success: boolean; message: string }> {
  try {
    await request(`/api/v1/bookings/${bookingId}/extend`, { 
      method: 'POST',
      body: JSON.stringify({ new_checkout_date: newCheckOutDate })
    });
    return { success: true, message: 'Stay extended successfully' };
  } catch (e: any) {
    return { success: false, message: e.message ?? 'Failed to extend stay' };
  }
}''',
    api_content,
    flags=re.DOTALL
)

# Replace createMembership
api_content = re.sub(
    r'export async function createMembership.*?\}',
    '''export async function createMembership(data: { name: string; phone: string; email: string }): Promise<{ success: boolean; message: string }> {
  try {
    await request(`/api/v1/guests/memberships`, { 
      method: 'POST',
      body: JSON.stringify(data)
    });
    return { success: true, message: 'Guest successfully enrolled in SkyNest Membership!' };
  } catch (e: any) {
    return { success: false, message: e.message ?? 'Failed to enroll member' };
  }
}''',
    api_content,
    flags=re.DOTALL
)

with open(api_ts_path, 'w', encoding='utf-8') as f:
    f.write(api_content)


# 2. Add enroll_membership to guest_repo.py
g_path = 'c:/Users/EX BOOK/Desktop/hotel/backend/app/repositories/guest_repo.py'
g_append = '''
    def enroll_membership(self, phone: str, name: str, email: str):
        if self.db is not None:
            try:
                with self.db.cursor(cursor_factory=RealDictCursor) as cursor:
                    # Check if guest exists
                    cursor.execute("SELECT guest_id FROM guests WHERE phone_number = %s", (phone,))
                    row = cursor.fetchone()
                    if row:
                        guest_id = row['guest_id']
                        # Set membership_id = 1
                        cursor.execute("UPDATE guests SET membership_id = 1 WHERE guest_id = %s", (guest_id,))
                    else:
                        cursor.execute(
                            "INSERT INTO guests (guest_id, membership_id, name, national_id, phone_number) VALUES ((SELECT COALESCE(MAX(guest_id),0)+1 FROM guests), 1, %s, 'PENDING', %s)",
                            (name, phone)
                        )
                    return True
            except Exception as e:
                print(f"Database error in enroll_membership: {e}")
                return False
        return True
'''
update_file(g_path, None, None, append=g_append)

# 3. Add enroll_membership to guest_service.py
gs_path = 'c:/Users/EX BOOK/Desktop/hotel/backend/app/services/guest_service.py'
gs_append = '''
    def enroll_membership(self, phone: str, name: str, email: str):
        success = self.guest_repo.enroll_membership(phone, name, email)
        if success:
            return {"success": True, "message": f"Guest {name} successfully enrolled in SkyNest Membership!"}
        return {"success": False, "message": "Failed to enroll member."}
'''
update_file(gs_path, None, None, append=gs_append)

# 4. Update schemas/guests.py
sch_path = 'c:/Users/EX BOOK/Desktop/hotel/backend/app/schemas/guests.py'
sch_append = '''
class CreateMembershipPayload(BaseModel):
    name: str
    phone: str
    email: str
'''
update_file(sch_path, None, None, append=sch_append)

# 5. Update api/private/guests.py
pg_path = 'c:/Users/EX BOOK/Desktop/hotel/backend/app/api/private/guests.py'
with open(pg_path, 'r', encoding='utf-8') as f:
    pg_content = f.read()

pg_content = pg_content.replace(')', ', CreateMembershipPayload)') if 'from app.schemas.guests import (' in pg_content else pg_content.replace('from app.schemas.guests import UpdatePhoneRequest', 'from app.schemas.guests import UpdatePhoneRequest, CreateMembershipPayload')

pg_append = '''
@router.post("/memberships")
def create_membership(
    payload: CreateMembershipPayload,
    guest_service: GuestService = Depends(get_guest_service)
):
    return guest_service.enroll_membership(payload.phone, payload.name, payload.email)
'''
with open(pg_path, 'w', encoding='utf-8') as f:
    f.write(pg_content + '\n' + pg_append)

print("All backend changes successfully applied!")
