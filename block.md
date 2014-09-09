
BitShares Toolkit Blockchain Spec
=================================

Donation addresses
------------------

Bitcoin: 1NfGejohzoVGffAD1CnCRgo9vApjCU2viY
Litecoin: LiUGs9sqH6GBHsvzpNtLCoyXB5aCDi9HsQ
Dogecoin: DTy5q7uUQ1whqyUrwC1LbhgqwKgovJT5R7
Protoshares (BitShares-PTS): PZxpdC8RqWsdU3pVJeobZY7JFKVPfNpy5z
BTSX: drltc

Notice
------

This is a DRAFT WIP spec.  This version has not yet been reviewed for correctness, completeness, or conformance to the behavior
of the code in the BitShares Toolkit, BTSX as released by DACSunlimited, or any other blockchain.

Changelog
---------

Testnet information:

    {
    "bitshares_toolkit_revision": "e6744e252c4f89c8d2156800edf55c483d6e8614",
    "bitshares_toolkit_revision_age": "79 hours ago",
    "fc_revision": "a0b3a9a92d28ec0b3a08b45b8c1449737f56dd34",
    "fc_revision_age": "6 days ago",
    "compile_date": "compiled on Sep  9 2014 at 01:22:59"
    }

Typographical conventions
-------------------------

A term's **definition** will appear in boldface type.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL
NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED",  "MAY", and
"OPTIONAL" in this document are to be interpreted as described in
RFC 2119.

The word "TODO" indicates content which is planned but not yet written.

Blocks
------

The core of BitShares Toolkit is the implementation of a ledger called the **blockchain**.  The blockchain is composed of units called **blocks**.
A block which obeys certain constraints we specify later is considered to be **valid**.  Checking these constraints is called **validation**.

An initial block is hardcoded in the client software; this block is called the **genesis block**.  Any valid non-genesis block `B` MUST
have its `previous` member refer to some valid block, say `A`; then we say that `A` is the **parent** of `B`.  Thus, the valid blocks
form a tree rooted at the genesis block.  The current blockchain is the longest path through this tree; if more than one such path
exists, the blockchain is said to have **forked**.

Block headers
-------------

Here is the structure of a block header:

    struct block_header
    {
       block_id_type        previous;
       uint32_t             block_num;
       fc::time_point_sec   timestamp;
       digest_type          transaction_digest;
       secret_hash_type     next_secret_hash;
       secret_hash_type     previous_secret;
    };

The `block_num` member is the height of the block.  The genesis block SHOULD have a `block_num` of 0; any non-genesis block MUST have its
`block_num` equal to its parent's `block_num` plus one.  Thus the `block_num` field indicates the height of the block.

The `timestamp` field specifies the time at which the block is generated.  The `timestamp` member of a block MUST be greater than the `timestamp`
member of its parent (TODO:  Plus interval?).  (TODO:  How do we check timestamp member against system clock?)

Delegates
---------

There are `BTS_BLOCKCHAIN_NUM_DELEGATES` nodes called **delegates** (which is defined as 101 delegates in `config.hpp`).

Every block in the blockchain must be signed by a delegate.  Which delegate(s) may sign a block is specified by the **delegate schedule**.

Slots
-----

The blockchain can only be extended by delegates.  Blockchains of traditional cryptocurrecies such as Bitcoin or Litecoin consist of a sequence of
**blocks**.  A BitShares Toolkit blockchain, by contrast, consists of a sequence of slots.  A **slot** is a placeholder data structure which MAY
contain a block.

TODO:  How is a missing block handled?

Genesis block
-------------

The first block in the blockchain is called the **genesis block**.  The genesis block is specified as `genesis.json`; the contents of this
block are hardcoded in the client.  (TODO:  Where, and how is the file generated?)  To comply with the license agreement, the `genesis.json`
for coins derived from the BitShares Toolkit code MUST have at least 10% of its genesis block reserved for proportional allocations for PTS
and AGS holders.

TODO:  Link to license restriction.

TODO:  What kinds of transactions are included in genesis block?

Signatures
----------

TODO:  How are signatures computed and validated?

Hashes
------

TODO:  How are block hashes computed?

Operations
----------

TODO:  What are the operations?  How do they work?

