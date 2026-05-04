"""Tests para el módulo blockchain: Block y Blockchain."""

import pytest

from src.blockchain import Block, Blockchain


class TestBlock:
    def test_hash_is_calculated_on_init(self):
        block = Block(0, {"key": "value"}, "0" * 64)
        assert block.hash == block.calculate_hash()

    def test_hash_changes_with_nonce(self):
        block = Block(0, {"key": "value"}, "0" * 64)
        original_hash = block.hash
        block.nonce += 1
        assert block.calculate_hash() != original_hash

    def test_to_dict_contains_required_fields(self):
        block = Block(1, {"tipo": "test"}, "abc123")
        d = block.to_dict()
        for field in ("index", "timestamp", "data", "previous_hash", "nonce", "hash"):
            assert field in d

    def test_to_dict_preserves_data(self):
        data = {"tipo": "registro_producto", "id": "P001"}
        block = Block(2, data, "prev_hash")
        assert block.to_dict()["data"] == data


class TestBlockchain:
    def test_genesis_block_created_on_init(self):
        bc = Blockchain()
        assert bc.chain_length == 1
        assert bc.chain[0].index == 0

    def test_add_block_increases_chain_length(self):
        bc = Blockchain(difficulty=1)
        bc.add_block({"tipo": "test"})
        assert bc.chain_length == 2

    def test_proof_of_work_respects_difficulty(self):
        bc = Blockchain(difficulty=2)
        block = bc.add_block({"dato": "xyz"})
        assert block.hash.startswith("00")

    def test_blocks_are_linked_by_hash(self):
        bc = Blockchain(difficulty=1)
        b1 = bc.add_block({"a": 1})
        b2 = bc.add_block({"b": 2})
        assert b2.previous_hash == b1.hash

    def test_validate_chain_is_true_for_valid_chain(self):
        bc = Blockchain(difficulty=1)
        bc.add_block({"x": 1})
        bc.add_block({"x": 2})
        assert bc.validate_chain() is True

    def test_validate_chain_detects_tampered_data(self):
        bc = Blockchain(difficulty=1)
        bc.add_block({"valor": 100})
        bc.chain[1].data = {"valor": 9999}
        assert bc.validate_chain() is False

    def test_validate_chain_detects_broken_link(self):
        bc = Blockchain(difficulty=1)
        bc.add_block({"a": 1})
        bc.chain[1].previous_hash = "hash_falso"
        assert bc.validate_chain() is False

    def test_get_block_returns_correct_block(self):
        bc = Blockchain(difficulty=1)
        bc.add_block({"n": 1})
        b = bc.get_block(1)
        assert b is not None
        assert b.index == 1

    def test_get_block_returns_none_for_out_of_range(self):
        bc = Blockchain(difficulty=1)
        assert bc.get_block(99) is None

    def test_to_dict_returns_list_of_dicts(self):
        bc = Blockchain(difficulty=1)
        bc.add_block({"test": True})
        chain_list = bc.to_dict()
        assert isinstance(chain_list, list)
        assert all(isinstance(b, dict) for b in chain_list)
