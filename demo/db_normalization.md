# Database Systems: Normalization Forms

Relational database normalization structures tables to reduce duplication and prevent insert, update, and delete anomalies.

- First Normal Form (1NF): Every column holds atomic values with no repeating groups.
- Second Normal Form (2NF): Satisfies 1NF and every non-key attribute depends on the full primary key.
- Third Normal Form (3NF): Satisfies 2NF with no transitive dependencies between non-key attributes.
- Boyce-Codd Normal Form (BCNF): Every determinant in a non-trivial functional dependency is a candidate superkey.
