import os
from app import create_app
from models import db
from models.user import User
from models.marketplace import CropListing
from models.scheme import GovernmentScheme
from datetime import datetime, timedelta
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
app = create_app()

def seed_database():
    with app.app_context():
        print("Clearing database...")
        db.drop_all()
        db.create_all()
        print("Database structure recreated.")

        # Famous Agricultural Schemes
        schemes = [
            GovernmentScheme(
                name="Pradhan Mantri Kisan Samman Nidhi (PM-KISAN)",
                ministry="Ministry of Agriculture and Farmers Welfare",
                description="PM-KISAN is a central sector scheme that provides financial assistance to all landholding farmers' families across the country.",
                benefits="Direct income support of ₹6,000 per year (in three equal installments of ₹2,000 every four months) to all landholding farmer families.",
                eligibility="All landholding farmers' families in the country (subject to certain exclusion criteria).",
                documents="Aadhaar Card, Land ownership documents, Bank account details.",
                apply_link="https://pmkisan.gov.in/RegistrationFormnew.aspx",
                category="Financial Support",
                is_state_specific=False,
                launch_year=2019
            ),
            GovernmentScheme(
                name="Pradhan Mantri Fasal Bima Yojana (PMFBY)",
                ministry="Ministry of Agriculture and Farmers Welfare",
                description="PMFBY is a crop insurance scheme launched to provide insurance coverage and financial support to farmers in the event of failure of any of the notified crops as a result of natural calamities, pests & diseases.",
                benefits="Financial support to farmers suffering crop loss/damage arising out of unforeseen events. Stabilization of the income of farmers to ensure their continuance in farming.",
                eligibility="All farmers including sharecroppers and tenant farmers growing the notified crops in the notified areas are eligible for coverage.",
                documents="Aadhaar Number, Land records (SOWING Certificate/RTC), Bank details (Passbook).",
                apply_link="https://pmfby.gov.in/farmer/registration",
                category="Insurance",
                is_state_specific=False,
                launch_year=2016
            ),
            GovernmentScheme(
                name="Kisan Credit Card (KCC) Scheme",
                ministry="Ministry of Finance",
                description="KCC aims at providing adequate and timely credit support from the banking system under a single window with flexible and simplified procedure for their cultivation and other needs.",
                benefits="Cheaper credit for farmers at a low interest rate (4%) with timely availability of funds.",
                eligibility="Farmers - Individual/Joint borrowers who are owner cultivators, tenant farmers, oral lessees, and sharecroppers.",
                documents="Aadhaar Card, Identity proof, Address proof, Land cultivation proof.",
                apply_link="https://eseva.csccloud.in/KCC/default.aspx",
                category="Financial Support",
                is_state_specific=False,
                launch_year=1998
            ),
            GovernmentScheme(
                name="Soil Health Card Scheme",
                ministry="Ministry of Agriculture and Farmers Welfare",
                description="This scheme helps farmers to know the health of their soil and use fertilizers accordingly. It improves soil health and fertility.",
                benefits="A Soil Health Card is issued periodically (every 2 years) to all farmers for their landholdings to indicate the nutrient status of their soil.",
                eligibility="Open to all farmers across the country.",
                documents="No specific documents required for registration; soil samples are collected from the field.",
                apply_link="https://www.soilhealth.dac.gov.in/FARMER/FarmerRegistration",
                category="Technical Support",
                is_state_specific=False,
                launch_year=2015
            ),
            GovernmentScheme(
                name="e-NAM (National Agriculture Market)",
                ministry="Ministry of Agriculture and Farmers Welfare",
                description="e-NAM is a pan-India electronic trading portal which networks the existing APMC mandis to create a unified national market for agricultural commodities.",
                benefits="One license for a trader valid across all markets in the state, single point levy of market fees, and electronic auction as a mode for price discovery.",
                eligibility="Farmers, Traders, and Buyers who wish to trade agricultural commodities.",
                documents="Aadhaar Card, Bank Passbook, Mobile Number.",
                apply_link="https://www.enam.gov.in/web/register/farmer-registration",
                category="Marketplace",
                is_state_specific=False,
                launch_year=2016
            ),
            GovernmentScheme(
                name="Pradhan Mantri Krishi Sinchai Yojana (PMKSY)",
                ministry="Ministry of Jal Shakti",
                description="PMKSY has been formulated with the vision of extending the coverage of irrigation 'Har Khet Ko Pani' and improving water use efficiency 'More crop per drop' in a focused manner.",
                benefits="Financial assistance for micro-irrigation systems (Drip and Sprinkler) to improve water usage.",
                eligibility="Farmers having their own land/leased land for at least 7 years are eligible for micro-irrigation systems.",
                documents="Aadhaar Card, Land documents (RTC), Bank Passbook, Passport photo.",
                apply_link="https://pmksy.gov.in/RegistrationForm.aspx",
                category="Technical Support",
                is_state_specific=False,
                launch_year=2015
            ),
            GovernmentScheme(
                name="E-Katha & Land Records (Karnataka)",
                ministry="Revenue Department, Government of Karnataka",
                description="Access digital records of land ownership, including RTC (Pani), KHP (E-Katha), and mutation records.",
                benefits="Digital access to RTC (Record of Rights, Tenancy and Crop Information) and Mutation reports to verify ownership and lease details.",
                eligibility="All land owners and interested parties in Karnataka.",
                documents="Survey Number, District, Taluk, Hobli, Village.",
                apply_link="https://landrecords.karnataka.gov.in/service2/",
                category="Records",
                is_state_specific=True,
                state="Karnataka"
            )
        ]

        db.session.bulk_save_objects(schemes)
        db.session.commit()
        print(f"Added {len(schemes)} famous schemes.")

if __name__ == '__main__':
    seed_database()
