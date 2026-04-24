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
                description="PM-KISAN provides financial assistance of ₹6,000 per year to all landholding farmer families.",
                benefits="Direct income support of ₹6,000 per year in three installments.",
                eligibility="All landholding farmers' families in the country.",
                documents="Aadhaar Card, Land records, Bank details.",
                apply_link="https://pmkisan.gov.in/RegistrationFormupdated.aspx",
                category="Financial Support",
                is_state_specific=False,
                launch_year=2019
            ),
            GovernmentScheme(
                name="Pradhan Mantri Fasal Bima Yojana (PMFBY)",
                ministry="Ministry of Agriculture and Farmers Welfare",
                description="PMFBY provides insurance coverage and financial support to farmers in case of crop failure due to natural calamities.",
                benefits="Financial support to farmers suffering crop loss. Stabilization of income.",
                eligibility="All farmers growing notified crops in notified areas.",
                documents="Aadhaar Number, Land records (SOWING Certificate/RTC), Bank details.",
                apply_link="https://pmfby.gov.in/selfRegistration",
                category="Insurance",
                is_state_specific=False,
                launch_year=2016
            ),
            GovernmentScheme(
                name="Rashtriya Krishi Vikas Yojana (RKVY)",
                ministry="Ministry of Agriculture",
                description="RKVY aims at making farming a remunerative economic activity through strengthening the farmer's effort and risk mitigation.",
                benefits="Financial assistance for agriculture infrastructure and allied sector projects.",
                eligibility="Farmers, SHGs, and cooperatives involved in agriculture.",
                documents="Project proposal, Land records, Identity proof.",
                apply_link="https://rkvy.da.gov.in/",
                category="Technical Support",
                is_state_specific=False,
                launch_year=2007
            ),
            GovernmentScheme(
                name="National Mission on Oilseeds and Oil Palm (NMOOP)",
                ministry="Ministry of Agriculture",
                description="NMOOP aims to increase production of oilseeds and oil palm to reduce dependency on edible oil imports.",
                benefits="Subsidies for seeds, fertilizers, and technology adoption in oilseed cultivation.",
                eligibility="Farmers interested in oilseed or oil palm cultivation.",
                documents="Aadhaar Card, Land records, Bank Passbook.",
                apply_link="https://nfsm.gov.in/nfmis/NM_Login.aspx",
                category="Production Support",
                is_state_specific=False,
                launch_year=2014
            ),
            GovernmentScheme(
                name="Kisan Credit Card (KCC) Scheme",
                ministry="Ministry of Finance",
                description="KCC provides adequate and timely credit support from the banking system for cultivation and other needs.",
                benefits="Cheaper credit at low interest rates (4%) with flexible repayment.",
                eligibility="Owner cultivators, tenant farmers, and sharecroppers.",
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
