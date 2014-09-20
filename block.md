
BitShares Toolkit Blockchain Spec
=================================

Donation addresses
------------------

- Bitcoin: 1NfGejohzoVGffAD1CnCRgo9vApjCU2viY
- Litecoin: LiUGs9sqH6GBHsvzpNtLCoyXB5aCDi9HsQ
- Dogecoin: DTy5q7uUQ1whqyUrwC1LbhgqwKgovJT5R7
- Protoshares (BitShares-PTS): PZxpdC8RqWsdU3pVJeobZY7JFKVPfNpy5z
- BTSX: drltc

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

Signed blocks
-------------

A **signed block** is a block which contains a delegate signature.  The signature algorithm is OpenSSL ECDSA.  The delegate signature
is considered to be part of the signed block's header, thus we have the following declaration:

   struct signed_block_header : public block_header
   {
       signature_type delegate_signature;
   };

Transaction lists
-----------------

A **transaction** is an atomic update to the global database state.  Each block contains zero or more transactions.  Thus we have
the following structure for a `full_block`:

   struct full_block : public signed_block_header
   {
       signed_transactions  user_transactions;
   };

The `full_block` is used in bulk downloads such as provided by the built-in chain server.  In the peer-to-peer code, when
a recipient can be expected to often already have some or all of the transactions in a block, we can save some
bandwidth by only transmitting the digests of transactions:

   struct digest_block : public signed_block_header
   {
       std::vector<transaction_id_type> user_transaction_ids;
   };

Of course, when receiving a `digest_block`, a validating node MUST obtain `user_transactions` to reconstruct the
`full_block` to perform validation.  This MAY be implemented by querying a local store of known pending transactions,
and then requesting unknown transactions from peers.

Transactions
------------

The transaction format consists of an expiration date, an optional `delegate_slate_id`, and zero or more `operation` objects:

   struct transaction
   {
      fc::time_point_sec          expiration;
      optional<slate_id_type>     delegate_slate_id;
      vector<operation>           operations;
   };

On-the-wire format
------------------

The following is a concise pseudocode description of the on-the-wire format of data structures.
A `vluint` is a variable-length unsigned integer, encoded in little-endian byte order using 7 bits
per byte; the most significant bit of each byte except the last is 1.  Integer data types are
little-endian.

Some elements are defined as types whose length can be changed by modifying `types.h` or
the `fc` library are noted in comments.  Derivative blockchains SHOULD NOT change the length
of fields.

    struct wire_operation
    {
        byte type;
        vluint num_data_bytes;
        byte data[num_data_bytes];
    };

    struct wire_signed_transaction
    {
        uint32 expiration;                      /* fc::time_point_sec */
        byte has_delegate_slate;
        uint64_t delegate_slate_id;             /* slate_id_type */
        vluint num_operations;
        wire_operation[num_operations] operations;
    };

    struct wire_block
    {
        // header
        byte[20] previous;                      /* block_id_type */
        uint32 block_num;
        uint32 timestamp;                       /* fc::time_point_sec */
        byte[20] transaction_digest;            /* digest_type */
        byte[20] next_secret_hash;              /* secret_hash_type */
        byte[20] previous_secret;               /* secret_hash_type */

        // body
        byte[65] delegate_signature;            /* fc::ecc::compact_signature */

        // transaction count
        vluint num_transactions;
        wire_signed_transaction[num_transactions] signed_transactions;
    };

Operations
----------

A transaction consists of zero or more **operations**.  An operation
contains some data, 

    enum operation_type_enum
    {
        null_op_type                = 0,

        /** balance operations */
        withdraw_op_type            = 1,
        deposit_op_type             = 2,

        /** account operations */
        register_account_op_type    = 3,
        update_account_op_type      = 4,
        withdraw_pay_op_type        = 5,

        /** asset operations */
        create_asset_op_type        = 6,
        update_asset_op_type        = 7,
        issue_asset_op_type         = 8,

        /** delegate operations */
        fire_delegate_op_type       = 9,

        /** proposal operations */
        submit_proposal_op_type     = 10,
        vote_proposal_op_type       = 11,

        /** market operations */
        bid_op_type                 = 12,
        ask_op_type                 = 13,
        short_op_type               = 14,
        cover_op_type               = 15,
        add_collateral_op_type      = 16,
        remove_collateral_op_type   = 17,

        define_delegate_slate_op_type = 18,

        update_feed_op_type          = 19
    };

Block identifiers
-----------------

The **block id** or **block identifier** of a signed block is a unique identifier derived from hashing the signed block's
header.  Specifically, the block identifier is computed the RIPEMD-160 digest of the SHA-512 hash of the signed block header.

The global database
-------------------

The blockchain is a log of the updates to the state shared by all nodes.  This shared state contains information on
everyone's accounts, coins, etc.  This spec will refer to that shared state as the **global database**.

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

Genesis state
-------------

In traditional cryptocoins such as Bitcoin, the first block in the blockchain is called the **genesis block**.  In BitShares X, the initial contents
of the global database are specified in `genesis.json` which is copied directly into the client executable by build scripts.  Some people refer to
the `genesis.json` data as the "genesis block" of a BitShares Toolkit blockchain.  However, for the purposes of this spec, the term
**genesis state** is preferred.

(TODO:  Where, and how is `genesis.json` generated?)

To comply with the license agreement, the `genesis.json` for coins derived from the BitShares Toolkit code MUST have at least 10% of its genesis
block reserved for proportional allocations for PTS and AGS holders.

TODO:  Link to license restriction.

