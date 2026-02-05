import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add services to path
sys.path.insert(0, str(Path(__file__).parent / "services/pipeline/src"))
sys.path.insert(0, str(Path(__file__).parent / "libs/termopol_db/src"))

from pipeline.ingest import PartiesIngestor, DeputiesIngestor, VotingsIngestor
from pipeline.transform.parties import PartyTransformer
from pipeline.transform.deputies import DeputyTransformer
from pipeline.transform.votings import VotingTransformer
from pipeline.transform.rollcalls import RollCallTransformer

def test_ingest():
    print("\n" + "=" * 60)
    print("TESTING INGEST STEP")
    print("=" * 60)
    
    # Test ingest parties from 2024
    print("\n" + "-" * 60)
    print("Testing PartiesIngestor...")
    print("-" * 60)
    parties = PartiesIngestor(datetime(2024, 1, 1))
    parties.ingest()
    
    # Test ingest deputies from 2024
    print("\n" + "-" * 60)
    print("Testing DeputiesIngestor...")
    print("-" * 60)
    deputies = DeputiesIngestor(datetime(2024, 1, 1))
    deputies.ingest()
    
    # Test ingest votings (includes rollcalls)
    print("\n" + "-" * 60)
    print("Testing VotingsIngestor (with rollcalls)...")
    print("-" * 60)
    votings = VotingsIngestor(datetime(2024, 1, 1))
    votings.ingest()

def test_transform():
    print("\n" + "=" * 60)
    print("TESTING TRANSFORM STEP")
    print("=" * 60)
    
    # Define date range for transform (last 24 hours from now)
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=1)
    
    print(f"\nDate range: {start_date} to {end_date}")
    
    # Transform parties
    print("\n" + "-" * 60)
    print("Testing PartyTransformer...")
    print("-" * 60)
    party_transformer = PartyTransformer()
    party_transformer.transform(start_date, end_date)
    print("✓ Party transformation completed")
    
    # Transform deputies
    print("\n" + "-" * 60)
    print("Testing DeputyTransformer...")
    print("-" * 60)
    deputy_transformer = DeputyTransformer()
    deputy_transformer.transform(start_date, end_date)
    print("✓ Deputy transformation completed")
    
    # Transform votings
    print("\n" + "-" * 60)
    print("Testing VotingTransformer...")
    print("-" * 60)
    voting_transformer = VotingTransformer()
    voting_transformer.transform(start_date, end_date)
    print("✓ Voting transformation completed")
    
    # Transform rollcalls (must be last as it depends on others)
    print("\n" + "-" * 60)
    print("Testing RollCallTransformer...")
    print("-" * 60)
    rollcall_transformer = RollCallTransformer()
    rollcall_transformer.transform(start_date, end_date)
    print("✓ RollCall transformation completed")

def main():
    try:
        # Uncomment to test ingest step
        # test_ingest()
        
        # Test transform step
        test_transform()
        
        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()