import re
from typing import List, Dict, Any
from dataclasses import dataclass, field

class MetricResult:
    name: str
    score: float
    details: Dict[str, Any] = field(default_factory=dict)

    def __repr__(self):
        return f"{self.name}: {self.score:.4f}"

def exact_match(predictions, references):
    def normalise(s):
        s = s.lower().strip()
        s = re.sub(r"[^\w\s]", "", s, flags=re.UNICODE)
        return s.strip()
    scores = [1.0 if normalise(p) == normalise(r) else 0.0
              for p, r in zip(predictions, references)]
    return MetricResult(
        name="exact_match",
        score=sum(scores) / len(scores) if scores else 0.0,
        details={"n_correct": int(sum(scores)), "n_total": len(scores)},
    )

def token_f1(predictions, references):
    def _f1(pred, ref):
        p_tok = pred.lower().split()
        r_tok = ref.lower().split()
        common = set(p_tok) & set(r_tok)
        if not common: return 0.0
        prec = len(common) / len(p_tok)
        rec  = len(common) / len(r_tok)
        return 2 * prec * rec / (prec + rec)
    scores = [_f1(p, r) for p, r in zip(predictions, references)]
    return MetricResult(name="token_f1",
                        score=sum(scores)/len(scores) if scores else 0.0)

def bleu(predictions, references):
    try:
        from sacrebleu.metrics import BLEU as SacreBLEU
        m = SacreBLEU(effective_order=True)
        r = m.corpus_score(predictions, [references])
        return MetricResult(name="bleu", score=r.score/100.0,
                            details={"sacrebleu": r.score})
    except Exception:
        scores = [len(set(p.lower().split()) & set(r.lower().split())) /
                  max(len(p.split()), 1) for p, r in zip(predictions, references)]
        return MetricResult(name="bleu", score=sum(scores)/len(scores) if scores else 0.0)

def chrf(predictions, references):
    try:
        from sacrebleu.metrics import CHRF
        m = CHRF()
        r = m.corpus_score(predictions, [references])
        return MetricResult(name="chrf", score=r.score/100.0)
    except Exception:
        def char_bigrams(s):
            return set(s[i:i+2] for i in range(len(s)-1))
        scores = []
        for p, r in zip(predictions, references):
            pg, rg = char_bigrams(p), char_bigrams(r)
            if not pg or not rg:
                scores.append(0.0); continue
            c = len(pg & rg)
            pr, rc = c/len(pg), c/len(rg)
            scores.append(2*pr*rc/(pr+rc) if (pr+rc) > 0 else 0.0)
        return MetricResult(name="chrf", score=sum(scores)/len(scores) if scores else 0.0)

def rouge_l(predictions, references):
    try:
        from rouge_score import rouge_scorer
        scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=False)
        scores = [scorer.score(r, p)["rougeL"].fmeasure
                  for p, r in zip(predictions, references)]
    except Exception:
        def lcs_score(a, b):
            a, b = a.lower().split(), b.lower().split()
            m, n = len(a), len(b)
            dp = [[0]*(n+1) for _ in range(m+1)]
            for i in range(1, m+1):
                for j in range(1, n+1):
                    dp[i][j] = dp[i-1][j-1]+1 if a[i-1]==b[j-1] else max(dp[i-1][j], dp[i][j-1])
            l = dp[m][n]
            p_ = l/max(len(a), 1); r_ = l/max(len(b), 1)
            return 2*p_*r_/(p_+r_) if (p_+r_) > 0 else 0.0
        scores = [lcs_score(p, r) for p, r in zip(predictions, references)]
    return MetricResult(name="rouge_l", score=sum(scores)/len(scores) if scores else 0.0)

def mcq_accuracy(predictions, references):
    import re
    def extract(text):
        text = text.strip().upper()
        m = re.search(r"\b([ABCD])\b", text)
        return m.group(1) if m else text[:1]
    scores = [1.0 if extract(p)==extract(r) else 0.0
              for p, r in zip(predictions, references)]
    return MetricResult(name="mcq_accuracy",
                        score=sum(scores)/len(scores) if scores else 0.0,
                        details={"n_correct": int(sum(scores)), "n_total": len(scores)})

def latency_stats(latencies_ms):
    if not latencies_ms:
        return MetricResult(name="latency_ms", score=0.0)
    s = sorted(latencies_ms); n = len(s)
    return MetricResult(name="latency_ms", score=sum(s)/n,
                        details={"mean_ms": sum(s)/n,
                                 "p50_ms": s[n//2], "p95_ms": s[int(n*.95)]})



