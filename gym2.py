from datetime import datetime, timedelta

# -------- Abstraction: Subscription Plan --------
class SubscriptionPlan:
    def __init__(self, name, duration, price):
        self.name = name
        self.duration = duration
        self.price = price

    def __str__(self):
        return f"{self.name} ({self.duration} days) - ${self.price}"

    def to_file(self):
        return f"{self.name},{self.duration},{self.price}\n"

# -------- Encapsulation & Abstraction: Member Class --------
class Member:
    def __init__(self, member_id, name, sex, phone, plan, join_date):
        self.__member_id = member_id
        self.__name = name
        self.__sex = sex
        self.__phone = phone
        self.__plan = plan
        self.__join_date = join_date
        self.__expiry_date = self.__calculate_expiry()

    def __calculate_expiry(self):
        return self.__join_date + timedelta(days=self.__plan.duration)

    @property
    def member_id(self): 
        return self.__member_id

    @property
    def phone(self): 
        return self.__phone

    @property
    def name(self): 
        return self.__name

    def update_phone(self, new_phone):
        if len(new_phone) >= 8:
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
        return (f"ID: {self.__member_id:<4} | Name: {self.__name:<10} | {self.__sex:<1} | "
                f"Phone: {self.__phone:<10} | Plan: {self.__plan.name:<10} | "
                f"Exp: {self.__expiry_date.date()} | {self.get_status()}")

    def to_file(self):
        return f"{self.__member_id},{self.__name},{self.__sex},{self.__phone},{self.__plan.name},{self.__plan.price},{self.__join_date.strftime('%Y-%m-%d')}\n"

# -------- Gym System Manager --------
class GymSystem:
    def __init__(self):
        self.__members = []
        self.__plans = {}
        # Load data in order: Plans first, then Members
        self.__load_plans()
        self.__load_members()

    # --- UPDATED: Save plans to file ---
    def add_subscription_plan(self):
        print("\n--- Create New Subscription Plan ---")
        name = input("Enter Plan Name: ").strip()
        try:
            duration = int(input("Enter Duration (days): "))
            price = float(input("Enter Price: $"))
            
            plan_id = str(len(self.__plans) + 1)
            self.__plans[plan_id] = SubscriptionPlan(name, duration, price)
            
            # Save the new plan to plans.txt
            self.__save_plans()
            print(f"✅ Plan '{name}' saved successfully!")
        except ValueError:
            print("❌ ERROR: Invalid input for duration or price.")

    def add_member(self):
        if not self.__plans:
            print("❌ ERROR: Please create a plan first (Option 1).")
            return

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
                print("✅ Member registered!")
            except ValueError:
                print("❌ Invalid date format!")

    def view_members(self):
        print("\n--- Current Members ---")
        if not self.__members: print("No records found.")
        for m in self.__members: print(m)

    def search_member(self):
        print("\n--- Search Member ---")
        phone = input("Enter Phone Number: ").strip()
        found = [m for m in self.__members if m.phone == phone]
        if found:
            for m in found: print(f"Found: {m}")
        else:
            print("❌ No member found.")

    def update_member(self):
        print("\n--- Update Member ---")
        search_id = input("Enter Member ID: ").strip()
        member = next((m for m in self.__members if m.member_id == search_id), None)
        if member:
            new_p = input(f"New Phone (blank to skip): ").strip()
            if new_p: member.update_phone(new_p)
            
            if self.__plans:
                print("\nChange Plan (blank to skip):")
                for k, v in self.__plans.items(): print(f"{k}. {v}")
                choice = input("Choice: ")
                if choice in self.__plans: member.update_plan(self.__plans[choice])
            
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
        else: print("❌ Not found.")

    # --- PERSISTENCE METHODS ---
    def __save_plans(self):
        with open("plans.txt", "w") as f:
            for p in self.__plans.values():
                f.write(p.to_file())

    def __load_plans(self):
        try:
            with open("plans.txt", "r") as f:
                for line in f:
                    d = line.strip().split(",")
                    if len(d) == 3:
                        p_id = str(len(self.__plans) + 1)
                        self.__plans[p_id] = SubscriptionPlan(d[0], int(d[1]), float(d[2]))
        except FileNotFoundError: pass

    def __save_members(self): 
        with open("members.txt", "w") as f:
            for m in self.__members: f.write(m.to_file())

    def __load_members(self): 
        try:
            with open("members.txt", "r") as f:
                for line in f:
                    d = line.strip().split(",")
                    if len(d) >= 7:
                        # Re-link plan by name from our loaded plans dictionary
                        plan_name = d[4]
                        matched_plan = next((p for p in self.__plans.values() if p.name == plan_name), None)
                        
                        # If no plan matches, create a temporary one so member can still be loaded
                        if not matched_plan:
                            matched_plan = SubscriptionPlan(d[4], 0, float(d[5]))
                            
                        dt = datetime.strptime(d[6], "%Y-%m-%d")
                        self.__members.append(Member(d[0], d[1], d[2], d[3], matched_plan, dt))
        except FileNotFoundError: pass

    def menu(self):
        while True:
            print("\n--- Gym Membership System ---")
            print("1. Add Plan | 2. Add Member | 3. View All | 4. Search | 5. Update | 6. Delete | 7. Exit")
            c = input("Option: ")
            if c == "1": self.add_subscription_plan()
            elif c == "2": self.add_member()
            elif c == "3": self.view_members()
            elif c == "4": self.search_member()
            elif c == "5": self.update_member()
            elif c == "6": self.delete_member()
            elif c == "7": break

if __name__ == "__main__":
    GymSystem().menu()
