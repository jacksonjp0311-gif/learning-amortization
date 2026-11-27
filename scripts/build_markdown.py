"""Build paper/whitepaper.md from paper/whitepaper.tex (run after the LaTeX build).

Cross-references are resolved from the LaTeX .aux file so that numbers in the
Markdown match the PDF exactly. Requires pandoc.
"""

import re
import subprocess
import sys
from pathlib import Path

PAPER = Path(__file__).resolve().parents[1] / "paper"
aux = (PAPER / "whitepaper.aux").read_text()
labels = {}
for key, num in re.findall(r"\\newlabel\{([^}@]+)\}\{\{([^}]*)\}", aux):
    labels[key] = num

NAMES = {"sec": ("Section", "Sections"), "prop": ("Proposition", "Propositions"), "def": ("Definition", "Definitions"),
         "tab": ("Table", "Tables"), "fig": ("Figure", "Figures"), "cor": ("Corollary", "Corollaries"),
         "eq": ("Eq.", "Eqs.")}


def num(k):
    if k not in labels:
        sys.exit(f"unresolved label {k}; build the PDF first")
    return labels[k]


def cref(m):
    keys = [k.strip() for k in m.group(2).split(",")]
    kind = keys[0].split(":")[0]
    one, many = NAMES[kind]
    nums = [f"({num(k)})" if kind == "eq" else num(k) for k in keys]
    name = one if len(nums) == 1 else many
    if m.group(1) == "C":
        name = name[0].upper() + name[1:]
    body = nums[0] if len(nums) == 1 else ", ".join(nums[:-1]) + " and " + nums[-1]
    return f"{name} {body}"


tex = (PAPER / "whitepaper.tex").read_text()
tex = re.sub(r"\\(c|C)ref\{([^}]*)\}", cref, tex)
tex = re.sub(r"\\eqref\{([^}]*)\}", lambda m: f"({num(m.group(1))})", tex)
# equation labels -> visible tags
tex = re.sub(r"\\label\{(eq:[^}]*)\}", lambda m: f"\\tag{{{num(m.group(1))}}}", tex)
# theorem bodies upright (avoids emphasis markers wrapping math on GitHub)
tex = tex.replace("\\newtheorem{definition}", "\\theoremstyle{definition}\n\\newtheorem{definition}", 1)
tex = tex.replace("\\includegraphics[width=0.62\\linewidth]{figures/synthetic_curve.pdf}",
                  "\\includegraphics{figures/synthetic_curve.png}")

tex = re.sub(r"\\begin\{tabularx\}\{\\linewidth\}\{(?:[^{}]|\{[^{}]*\{[^{}]*\}[^{}]*\}|\{[^{}]*\})*\}",
             lambda m: "\\begin{tabular}{lll}" if "p{2.6cm}" in m.group(0) else "\\begin{tabular}{ll}", tex)
tex = tex.replace("\\end{tabularx}", "\\end{tabular}")
tex = tex.replace("\\|", "\\Vert ").replace("\\{", "\\lbrace ").replace("\\}", "\\rbrace ")

md = subprocess.run(
    ["pandoc", "-f", "latex", "-t", "gfm", "--citeproc", "--bibliography", str(PAPER / "refs.bib"),
     "--wrap=none", "--number-sections", "--shift-heading-level-by=1"],
    input=tex, capture_output=True, text=True, cwd=PAPER, check=True,
).stdout

# display math on its own lines for GitHub
md = re.sub(r"\s*\$\$(.+?)\$\$\s*", lambda m: "\n\n$$\n" + m.group(1).strip() + "\n$$\n\n", md, flags=re.S)
md = re.sub(r"\n{3,}", "\n\n", md)
md = re.sub(r"<a href=\"#[^\"]*\" data-reference-type=\"[^\"]*\"\s*data-reference=\"[^\"]*\">([^<]*)</a>", r"\1", md)

# numbered headings, paragraph headings as bold run-in text
out, sec, sub, appendix = [], 0, 0, False
for line in md.split("\n"):
    if line.startswith("## ") and not line.startswith("## Abstract"):
        title = line[3:]
        if title == "Notation":
            appendix = True
            out.append("## Appendix A. Notation")
            continue
        sec, sub = sec + 1, 0
        out.append(f"## {sec}. {title}")
    elif line.startswith("### "):
        sub += 1
        out.append(f"### {sec}.{sub} {line[4:]}")
    elif line.startswith("##### "):
        out.append(f"**{line[6:]}**")
    else:
        out.append(line)
md = "\n".join(out)
# Proposition 1 uses roman item labels in the PDF; mirror them
blk = md.index("**Proposition 1**")
end = md.index("</div>", blk)
part = md[blk:end]
for k, r in enumerate(["i", "ii", "iii", "iv", "v"], start=1):
    part = part.replace(f"\n{k}.  *", f"\n({r}) *", 1)
md = md[:blk] + part + md[end:]
md = md.replace('<div id="refs"', '## References\n\n<div id="refs"', 1)

header = (
    "# Learning Amortization: Measuring Whether Learning Makes Future Learning Cheaper\n\n"
    "**James Jackson** · Working paper v0.1 · November 2026 · "
    "[PDF](whitepaper.pdf) (canonical; this Markdown is generated from the LaTeX source by "
    "`scripts/build_markdown.py`)\n\n"
)
abstract = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", tex, re.S).group(1)
abs_md = subprocess.run(["pandoc", "-f", "latex", "-t", "gfm", "--wrap=none"], input=abstract,
                        capture_output=True, text=True, check=True).stdout
(PAPER / "whitepaper.md").write_text(header + "## Abstract\n\n" + abs_md.strip() + "\n\n" + md.strip() + "\n")
print("wrote", PAPER / "whitepaper.md")
