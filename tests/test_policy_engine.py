"""
Unit tests for the policy engine. Zero DB dependency by design — the
whole point of separating policy from the AI layer is that it can be
tested and verified in complete isolation.

Run with: pytest -v
"""
from types import SimpleNamespace

from app.services import policy_engine


def make_customer(**overrides):
    defaults = dict(
        customer_id="C_TEST", verification_status="verified",
        account_age_months=24, card_status="active", current_credit_limit=50000,
    )
    defaults.update(overrides)
    return SimpleNamespace(**defaults)


class TestFeeReversalEligibility:
    def test_approves_small_recent_fee_for_established_account(self):
        customer = make_customer(account_age_months=24)
        approved, reason = policy_engine.check_fee_reversal_eligibility(
            customer, fee_amount=199.0, days_since_charge=3, prior_reversals_90d=0)
        assert approved is True
        assert reason == "Eligible for automatic reversal"

    def test_rejects_new_account(self):
        customer = make_customer(account_age_months=2)
        approved, reason = policy_engine.check_fee_reversal_eligibility(
            customer, fee_amount=199.0, days_since_charge=3, prior_reversals_90d=0)
        assert approved is False
        assert "account age" in reason.lower()

    def test_rejects_amount_over_threshold(self):
        customer = make_customer()
        approved, reason = policy_engine.check_fee_reversal_eligibility(
            customer, fee_amount=5000.0, days_since_charge=3, prior_reversals_90d=0)
        assert approved is False
        assert "exceeds auto-approval threshold" in reason

    def test_rejects_prior_reversal_within_90_days(self):
        customer = make_customer()
        approved, reason = policy_engine.check_fee_reversal_eligibility(
            customer, fee_amount=100.0, days_since_charge=3, prior_reversals_90d=1)
        assert approved is False
        assert "prior reversal" in reason.lower()

    def test_rejects_stale_charge(self):
        customer = make_customer()
        approved, reason = policy_engine.check_fee_reversal_eligibility(
            customer, fee_amount=100.0, days_since_charge=90, prior_reversals_90d=0)
        assert approved is False
        assert "60-day" in reason


class TestCardReplacementEligibility:
    def test_approves_damaged_card_for_verified_customer(self):
        customer = make_customer(card_status="damaged")
        approved, reason = policy_engine.check_card_replacement_eligibility(customer, "damaged card")
        assert approved is True

    def test_escalates_lost_card(self):
        customer = make_customer()
        approved, reason = policy_engine.check_card_replacement_eligibility(customer, "lost")
        assert approved is False
        assert "re-verification" in reason

    def test_escalates_unverified_customer(self):
        customer = make_customer(verification_status="unverified")
        approved, reason = policy_engine.check_card_replacement_eligibility(customer, "damaged")
        assert approved is False
        assert "not verified" in reason


class TestCreditLimitEligibility:
    def test_approves_within_cap_for_established_verified_account(self):
        customer = make_customer(account_age_months=24)
        approved, reason = policy_engine.check_credit_limit_eligibility(customer, 10000)
        assert approved is True

    def test_rejects_amount_over_cap(self):
        customer = make_customer()
        approved, reason = policy_engine.check_credit_limit_eligibility(customer, 50000)
        assert approved is False
        assert "auto-approval cap" in reason

    def test_rejects_young_account(self):
        customer = make_customer(account_age_months=4)
        approved, reason = policy_engine.check_credit_limit_eligibility(customer, 5000)
        assert approved is False
        assert "account age" in reason.lower()
