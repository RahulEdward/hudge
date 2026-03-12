"""Backtest report generator — JSON metrics, trade log, and strategy summary."""

import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger


class ReportGenerator:
    """Generates backtest reports in JSON format with comprehensive metrics."""

    REPORT_DIR = "database/reports"

    def __init__(self):
        os.makedirs(self.REPORT_DIR, exist_ok=True)

    def generate(
        self,
        metrics: Dict[str, Any],
        trade_log: List[Dict],
        equity_curve: List[Dict],
        strategy_info: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Generate a full backtest report."""
        report = {
            "generated_at": datetime.now().isoformat(),
            "strategy": strategy_info or {},
            "metrics": self._format_metrics(metrics),
            "trade_summary": self._summarize_trades(trade_log),
            "equity_curve_length": len(equity_curve),
            "equity_curve": equity_curve[-100:] if len(equity_curve) > 100 else equity_curve,
            "trade_log": trade_log[-500:] if len(trade_log) > 500 else trade_log,
        }

        # Save to file
        report_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.REPORT_DIR, f"report_{report_id}.json")
        try:
            with open(report_path, "w") as f:
                json.dump(report, f, indent=2, default=str)
            report["report_path"] = report_path
        except Exception as e:
            logger.error(f"Failed to save report: {e}")

        return report

    def _format_metrics(self, metrics: Dict) -> Dict:
        formatted = {}
        for key, value in metrics.items():
            if isinstance(value, float):
                formatted[key] = round(value, 4)
            else:
                formatted[key] = value
        return formatted

    def _summarize_trades(self, trade_log: List[Dict]) -> Dict:
        if not trade_log:
            return {"total_trades": 0}

        pnl_trades = [t for t in trade_log if "pnl" in t]
        wins = [t for t in pnl_trades if t["pnl"] > 0]
        losses = [t for t in pnl_trades if t["pnl"] <= 0]

        total_profit = sum(t["pnl"] for t in wins) if wins else 0
        total_loss = abs(sum(t["pnl"] for t in losses)) if losses else 0

        return {
            "total_trades": len(trade_log),
            "closed_trades": len(pnl_trades),
            "winning_trades": len(wins),
            "losing_trades": len(losses),
            "win_rate": round(len(wins) / len(pnl_trades) * 100, 1) if pnl_trades else 0,
            "total_profit": round(total_profit, 2),
            "total_loss": round(total_loss, 2),
            "net_pnl": round(total_profit - total_loss, 2),
            "profit_factor": round(total_profit / total_loss, 2) if total_loss > 0 else float("inf"),
            "avg_win": round(total_profit / len(wins), 2) if wins else 0,
            "avg_loss": round(total_loss / len(losses), 2) if losses else 0,
            "largest_win": round(max(t["pnl"] for t in wins), 2) if wins else 0,
            "largest_loss": round(min(t["pnl"] for t in losses), 2) if losses else 0,
            "total_commission": round(sum(t.get("commission", 0) for t in trade_log), 2),
        }

    def generate_csv(self, trade_log: List[Dict], output_path: str = None) -> str:
        """Export trade log as CSV."""
        if not output_path:
            output_path = os.path.join(self.REPORT_DIR, f"trades_{datetime.now():%Y%m%d_%H%M%S}.csv")

        try:
            import csv
            if trade_log:
                keys = trade_log[0].keys()
                with open(output_path, "w", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=keys)
                    writer.writeheader()
                    writer.writerows(trade_log)
        except Exception as e:
            logger.error(f"CSV export failed: {e}")

        return output_path
