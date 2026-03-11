from datetime import datetime, timedelta


class SubscriptionPlan:
    def __init__(self, name, duration, price):
        self.name = name
        self.duration = duration
        self.price = price

    def __str__(self):
        # Provides a clean string representation for the menu
        return f"{self.name} ({self.duration} days) - ${self.price}"

# -------- Encapsulation & Abstraction: Member Class --------
class Member:
    def __init__(self, member_id, name, sex, phone, plan, join_date):
        # Encapsulation: Private attributes (__) cannot be accessed directly from outside
        self.__member_id = member_id
        self.__name = name
        self.__sex = sex
        self.__phone = phone
        self.__plan = plan
        self.__join_date = join_date
        self.__expiry_date = self.__calculate_expiry()

    # Abstraction: Hiding the complex date calculation logic
    def __calculate_expiry(self):
        return self.__join_date + timedelta(days=self.__plan.duration)

    # Encapsulation: Getter methods (Read-only access)
    @property
    def member_id(self): return self.__member_id

    @property
    def phone(self): return self.__phone

    @property
    def name(self): return self.__name

    # Encapsulation: Controlled update methods (Setters)
    def update_phone(self, new_phone):
        if len(new_phone) >= 8: # Basic validation rule
            self.__phone = new_phone
            return True
        return False

    def update_plan(self, new_plan):
        self.__plan = new_plan
        self.__expiry_date = self.__calculate_expiry()

    def get_status(self):
        if datetime.now() <= self.__expiry_date:
            return "Active"
        return "Expired"

    def __str__(self):
        # Formatted string for the 'View Members' list
        return (f"ID: {self.__member_id:<4} | Name: {self.__name:<10} | {self.__sex:<1} | "
                f"Phone: {self.__phone:<10} | Plan: {self.__plan.name:<10} | "
                f"Exp: {self.__expiry_date.date()} | {self.get_status()}")

    def to_file(self):
        # Format used for saving data to members.txt
        return f"{self.__member_id},{self.__name},{self.__sex},{self.__phone},{self.__plan.name},{self.__plan.price},{self.__join_date.strftime('%Y-%m-%d')}\n"

# -------- Gym System Manager --------
class GymSystem:
    def __init__(self):
        self.__members = [] # Encapsulated list of member objects
        self.__plans = {
            "1": SubscriptionPlan("Monthly", 30, 30),
            "2": SubscriptionPlan("Quarterly", 90, 80),
            "3": SubscriptionPlan("Yearly", 365, 300)
        }
        self.__load_members()

    def add_member(self):
        print("\n--- Add Member ---")
        mid = input("Enter Member ID: ").strip()

        if any(m.member_id == mid for m in self.__members):
            print(f"❌ ERROR: ID {mid} already exists!")
            return

        name = input("Enter Name: ")
        sex = input("Enter Sex (M/F): ").upper()
        phone = input("Enter Phone: ").strip()
        
        if any(m.phone == phone for m in self.__members):
            print(f"❌ ERROR: Phone already registered!")
            return

        print("\nSelect Plan:")
        for k, v in self.__plans.items(): print(f"{k}. {v}")
        choice = input("Choice: ")
        
        if choice in self.__plans:
            try:
                date_in = input("Enter Join Date (DD-MM-YYYY): ").strip()
                join_date = datetime.strptime(date_in, "%d-%m-%Y")
                new_m = Member(mid, name, sex, phone, self.__plans[choice], join_date)
                self.__members.append(new_m)
                self.__save_members()
                print("✅ Member registered successfully!")
            except ValueError:
                print("❌ Invalid date format!")

    def view_members(self):
        print("\n--- Current Members ---")
        if not self.__members:
            print("No records found.")
        for m in self.__members:
            print(m)

    def search_member(self):
        print("\n--- Search Member ---")
        phone = input("Enter Phone Number: ").strip()
        found = [m for m in self.__members if m.phone == phone]
        if found:
            for m in found: print(f"Found: {m}")
        else:
            print("❌ No member found with that phone number.")

    def update_member(self):
        print("\n--- Update Member ---")
        search_id = input("Enter Member ID: ").strip()
        member = next((m for m in self.__members if m.member_id == search_id), None)
        
        if member:
            new_p = input(f"New Phone (blank to skip): ").strip()
            if new_p:
                if any(m.phone == new_p and m.member_id != search_id for m in self.__members):
                    print("❌ Error: Phone already in use.")
                else:
                    member.update_phone(new_p)

            print("\nChange Plan (blank to skip):")
            for k, v in self.__plans.items(): print(f"{k}. {v}")
            choice = input("Choice: ")
            if choice in self.__plans:
                member.update_plan(self.__plans[choice])
            
            self.__save_members()
            print("✅ Update successful.")
        else:
            print("❌ Member not found.")

    def delete_member(self):
        print("\n--- Delete Member ---")
        phone = input("Enter Phone to remove: ").strip()
        member = next((m for m in self.__members if m.phone == phone), None)
        if member:
            self.__members.remove(member)
            self.__save_members()
            print(f"✅ Member deleted.")
        else:
            print("❌ Not found.")

    def __save_members(self): 
        with open("members.txt", "w") as f:
            for m in self.__members: f.write(m.to_file())

    def __load_members(self): 
        try:
            with open("members.txt", "r") as f:
                for line in f:
                    d = line.strip().split(",")
                    if len(d) >= 7:
                        dur = 30 if d[4] == "Monthly" else 90 if d[4] == "Quarterly" else 365
                        p = SubscriptionPlan(d[4], dur, float(d[5]))
                        dt = datetime.strptime(d[6], "%Y-%m-%d")
                        self.__members.append(Member(d[0], d[1], d[2], d[3], p, dt))
        except FileNotFoundError:
            pass

    def menu(self):
        while True:
            print("\n--- Gym Membership System ---")
            print("1. Add Member | 2. View All | 3. Search | 4. Update | 5. Delete | 6. Exit")
            c = input("Option: ")
            if c == "1": self.add_member()
            elif c == "2": self.view_members()
            elif c == "3": self.search_member()
            elif c == "4": self.update_member()
            elif c == "5": self.delete_member()
            elif c == "6": break

if __name__ == "__main__":
    GymSystem().menu()
