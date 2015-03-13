# Converting From RasMol #

| **RasMol Command** | **Corresponding Cinemol Command(s)** | **Description** |
|:-------------------|:-------------------------------------|:----------------|
| ` center {<expression>} ` | `  ` | Set center of rotation |
| ` select * ` | ` select("*") `| Select all residues |
| ` select 4 ` | ` select("4") ` | Select residue 4 of all chains |
| `  ` | ` select("5-8") ` | Select residues 5,6,7,and 8 of all chains|
| `  ` | ` select("cys") ` | Select all cysteine residues|
| ` select alaA.c? ` | ` select("alaA.c*") ` | Select all alanine carbons in chain A|
| `  ` | ` select(".c*") `| Select all carbon atoms |
| ` color yellow ` | ` color(col.yellow) ` | Color previously selected atoms yellow|