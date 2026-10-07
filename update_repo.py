import sys
import re

try:
    with open('c:/Users/EX BOOK/Desktop/hotel/backend/app/repositories/booking_repo.py', 'r', encoding='utf-8') as f:
        content = f.read()

    new_code = '''    def add_service_to_booking(self, booking_id: int, payload):
        if self.db is not None:
            try:
                with self.db.cursor() as cursor:
                    # 1. Update the grand total in billing_summary
                    cursor.execute(
                        "UPDATE billing_summary SET total_service_charges = COALESCE(total_service_charges, 0) + %s, grand_total = COALESCE(grand_total, 0) + %s WHERE booking_id = %s",
                        (payload.service_total, payload.service_total, booking_id)
                    )
                    
                    # 2. Insert into service_charges (Finds service_id using service_name automatically!)
                    cursor.execute(
                        """
                        INSERT INTO service_charges (service_log_id, booking_id, service_id, service_dates, service_total)
                        SELECT 
                            (SELECT COALESCE(MAX(service_log_id), 0) + 1 FROM service_charges), 
                            %s, 
                            service_id, 
                            %s, 
                            %s 
                        FROM service_catalogue 
                        WHERE service_name = %s
                        """,
                        (booking_id, payload.service_dates, payload.service_total, payload.service_name)
                    )
            except Exception as e:
                print(f"Database error in add_service: {e}")
                pass
                
        # In-memory fallback if the database is offline
        for b in self._bookings:
            if b.get("booking_id") == booking_id:
                if "service_charges" not in b:
                    b["service_charges"] = []
                b["service_charges"].append({
                    "service_name": payload.service_name,
                    "service_total": payload.service_total,
                    "service_dates": payload.service_dates
                })
                b["grand_total"] = b.get("grand_total", 0.0) + payload.service_total
                break'''

    content = re.sub(r'    def add_service_to_booking.*?cursor\.execute\("INSERT INTO service_charges "\)', new_code, content, flags=re.DOTALL)
    
    with open('c:/Users/EX BOOK/Desktop/hotel/backend/app/repositories/booking_repo.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print('Replaced via regex!')
except Exception as e:
    print('Error:', e)
