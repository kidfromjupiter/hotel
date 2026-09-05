-- 1. Independent Tables
CREATE TABLE SkyNest_Membership (
    Membership_ID INT PRIMARY KEY,
    Membership_Name VARCHAR(255),
    Room_Discount_Percentage DECIMAL(10,2),
    Service_Discount_Percentage DECIMAL(10,2)
);

CREATE TABLE Tax_Policies (
    Tax_ID INT PRIMARY KEY,
    Tax_Name VARCHAR(20),
    Active BOOLEAN,
    Tax_Percentage DECIMAL(10,2)
);

CREATE TABLE Branches (
    Branch_ID INT PRIMARY KEY,
    Branch_name VARCHAR(255)
);

CREATE TABLE Room_Types (
    Room_Type_ID VARCHAR(50) PRIMARY KEY,
    Daily_Rate DECIMAL(10,2)
);

CREATE TABLE Amenities (
    Amentity_ID INT PRIMARY KEY,
    Amentity_Name VARCHAR(255)
);

CREATE TABLE Service_Catalogue (
    Service_ID INT PRIMARY KEY,
    Service_name VARCHAR(255),
    Day_Rate DECIMAL(10,2)
);

-- 2. First-level Dependent Tables
CREATE TABLE Guests (
    Guest_ID INT PRIMARY KEY,
    Membership_ID INT,
    Name VARCHAR(255),
    National_ID VARCHAR(20),
    Phone_Number INT,
    FOREIGN KEY (Membership_ID) REFERENCES SkyNest_Membership(Memebership_ID)
);

CREATE TABLE Room_Details (
    Room_Number SMALLINT,
    Branch_ID INT,
    Room_Type_ID VARCHAR(50),
    Room_Status VARCHAR(50),
    PRIMARY KEY (Room_Number, Branch_ID),
    FOREIGN KEY (Branch_ID) REFERENCES Branches(Branch_ID),
    FOREIGN KEY (Room_Type_ID) REFERENCES Room_Types(Room_Type_ID)
);

CREATE TABLE Room_Amenities (
    Amentity_ID INT,
    Room_Type VARCHAR(50),
    PRIMARY KEY (Amentity_ID, Room_Type),
    FOREIGN KEY (Amentity_ID) REFERENCES Amenities(Amentity_ID),
    FOREIGN KEY (Room_Type) REFERENCES Room_Types(Room_Type_ID)
);

-- 3. Bookings and onward
CREATE TABLE Booking (
    Booking_ID BIGINT PRIMARY KEY,
    Room_Number SMALLINT,
    Branch_ID INT,
    Guest_ID INT,
    Booking_Status VARCHAR(50),
    Start_Date DATE,
    End_Date DATE,
    Checked_In_Time TIME,
    Checked_Out_Time TIME,
    Adult_Count INT,
    Children_Count INT,
    FOREIGN KEY (Room_Number, Branch_ID) REFERENCES Room_Details(Room_Number, Branch_ID),
    FOREIGN KEY (Guest_ID) REFERENCES Guests(Guest_ID)
);

CREATE TABLE Billing_Summary (
    Invoice_ID UUID PRIMARY KEY,
    Payment_Method VARCHAR(50),
    Booking_ID BIGINT,
    Total_Room_Charges DECIMAL(10,2),
    Total_Service_Charges DECIMAL(10,2),
    Total_Tax_Amount DECIMAL(10,2),
    Grand_Total DECIMAL(10,2),
    Amount_Paid DECIMAL(10,2),
    Payment_Status VARCHAR(50),
    FOREIGN KEY (Booking_ID) REFERENCES Booking(Booking_ID)
);

CREATE TABLE Service_Charges (
    Service_Log_ID INT PRIMARY KEY,
    Booking_ID BIGINT, 
    Service_ID INT,
    Service_Dates INT,
    Service_Total DECIMAL(10,2),
    FOREIGN KEY (Booking_ID) REFERENCES Booking(Booking_ID),
    FOREIGN KEY (Service_ID) REFERENCES Service_Catalogue(Service_ID)
);

CREATE TABLE Invoice_Taxes (
    Invoice_ID UUID,
    Tax_ID INT,
    Calculated_Amount DECIMAL(10,2),
    PRIMARY KEY (Invoice_ID, Tax_ID),
    FOREIGN KEY (Invoice_ID) REFERENCES Billing_Summary(Invoice_ID),
    FOREIGN KEY (Tax_ID) REFERENCES Tax_Policies(Tax_ID)
);

CREATE TABLE Booking_Extra_Amenities (
    Booking_ID BIGINT,
    Amentity_ID INT,
    Quantity INT,
    PRIMARY KEY (Booking_ID, Amentity_ID),
    FOREIGN KEY (Booking_ID) REFERENCES Booking(Booking_ID),
    FOREIGN KEY (Amentity_ID) REFERENCES Amenities(Amentity_ID)
);

ALTER TABLE transactions 
ADD COLUMN payment_method VARCHAR(50),
ADD CONSTRAINT fk_invoice FOREIGN KEY (invoice_id) REFERENCES Billing_Summary(Invoice_ID);