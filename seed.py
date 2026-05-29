"""
Seed script for local TigerBeetle development.
Creates test accounts and transfers so the tap has data to extract.
Run once before using the VS Code debugger:
    python seed.py
"""
import os
import tigerbeetle as tb

TB_ADDRESS = os.getenv("TB_ADDRESS", "3000")
CLUSTER_ID = 0


def main() -> None:
    with tb.ClientSync(cluster_id=CLUSTER_ID, replica_addresses=TB_ADDRESS) as client:

        # ── 1. Create accounts ──────────────────────────────────────────────
        accounts = [
            tb.Account(
                id=1,
                ledger=1,
                code=1,
                user_data_128=1001,
                user_data_64=2001,
                user_data_32=3001,
                flags=0,
            ),
            tb.Account(
                id=2,
                ledger=1,
                code=2,
                user_data_128=1002,
                user_data_64=2002,
                user_data_32=3002,
                flags=0,
            ),
            tb.Account(
                id=3,
                ledger=1,
                code=1,
                user_data_128=1003,
                user_data_64=2003,
                user_data_32=3003,
                flags=0,
            ),
        ]

        results = client.create_accounts(accounts)
        for i, result in enumerate(results):
            if result.status == tb.CreateAccountStatus.EXISTS:
                print(f"  [INFO] Account at index {i} already exists, skipping.")
            else:
                print(f"  [ERROR] Account at index {i} failed: {result.status}")
        print(f"✓ Accounts processed ({len(accounts)} submitted)")

        # ── 2. Create transfers ─────────────────────────────────────────────
        transfers = [
            tb.Transfer(
                id=1,
                debit_account_id=1,
                credit_account_id=2,
                ledger=1,
                code=1,
                amount=500,
                pending_id=0,
                user_data_128=9001,
                user_data_64=8001,
                user_data_32=7001,
                timeout=0,
                flags=0,
                timestamp=0,
            ),
            tb.Transfer(
                id=2,
                debit_account_id=2,
                credit_account_id=3,
                ledger=1,
                code=1,
                amount=200,
                pending_id=0,
                user_data_128=9002,
                user_data_64=8002,
                user_data_32=7002,
                timeout=0,
                flags=0,
                timestamp=0,
            ),
            tb.Transfer(
                id=3,
                debit_account_id=3,
                credit_account_id=1,
                ledger=1,
                code=1,
                amount=100,
                pending_id=0,
                user_data_128=9003,
                user_data_64=8003,
                user_data_32=7003,
                timeout=0,
                flags=0,
                timestamp=0,
            ),
        ]

        results = client.create_transfers(transfers)
        for i, result in enumerate(results):
            if result.status == tb.CreateTransferStatus.EXISTS:
                print(f"  [INFO] Transfer at index {i} already exists, skipping.")
            else:
                print(f"  [ERROR] Transfer at index {i} failed: {result.status}")
        print(f"✓ Transfers processed ({len(transfers)} submitted)")

        # ── 3. Verify ───────────────────────────────────────────────────────
        print("\n── Account state after seeding ─────────────────────────────────")
        fetched = client.lookup_accounts([1, 2, 3])
        for acc in fetched:
            print(
                f"  id={acc.id:<4} ledger={acc.ledger} code={acc.code} "
                f"debits_posted={acc.debits_posted:<6} credits_posted={acc.credits_posted:<6} "
                f"debits_pending={acc.debits_pending:<6} credits_pending={acc.credits_pending:<6} "
                f"user_data_128={acc.user_data_128} user_data_64={acc.user_data_64} "
                f"user_data_32={acc.user_data_32} flags={acc.flags} timestamp={acc.timestamp}"
            )

        print("\n── Done. TigerBeetle is ready for the tap. ─────────────────────")


if __name__ == "__main__":
    main()