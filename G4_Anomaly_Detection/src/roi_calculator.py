"""
G4 - ROI Calculator Module
Calculates Return on Investment for anomaly detection system
"""

import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from src.database import DatabaseConnection
from config.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ROICalculator:
    """
    Calculates financial impact and ROI of the anomaly detection system
    """
    
    def __init__(self):
        self.db = DatabaseConnection()
        
        # Costs from configuration
        self.cost_prevented_failure = Config.COST_PREVENTED_FAILURE
        self.cost_false_alarm = Config.COST_FALSE_ALARM
        self.energy_cost_per_kwh = Config.ENERGY_COST_PER_KWH
        
        # Assumptions for ROI calculation
        self.true_positive_rate = 0.85  # 85% of real anomalies detected
        self.false_positive_rate = 0.05  # 5% false alarm rate
        self.failure_prevention_rate = 0.70  # 70% of detected anomalies prevent failures
    
    def connect(self):
        """Connect to database"""
        return self.db.connect()
    
    def disconnect(self):
        """Disconnect from database"""
        self.db.disconnect()
    
    def get_anomaly_data(self, start_date=None, end_date=None):
        """
        Retrieve anomaly detection data from database
        
        Args:
            start_date (str): Start date for analysis (YYYY-MM-DD)
            end_date (str): End date for analysis (YYYY-MM-DD)
            
        Returns:
            pd.DataFrame: Anomaly data
        """
        try:
            query = """
            SELECT 
                ts,
                global_active_power_kw,
                voltage_v,
                is_anomaly,
                anomaly_score
            FROM power_consumption
            WHERE scored_at IS NOT NULL
            """
            
            if start_date:
                query += f" AND ts >= '{start_date}'"
            if end_date:
                query += f" AND ts <= '{end_date}'"
            
            query += " ORDER BY ts"
            
            df = pd.read_sql(query, self.db.engine)
            logger.info(f"✓ Retrieved {len(df)} records for ROI analysis")
            
            return df
        
        except Exception as e:
            logger.error(f"Error retrieving anomaly data: {e}")
            return pd.DataFrame()
    
    def calculate_basic_metrics(self, df):
        """
        Calculate basic detection metrics
        
        Args:
            df (pd.DataFrame): Anomaly data
            
        Returns:
            dict: Basic metrics
        """
        total_records = len(df)
        total_anomalies = df['is_anomaly'].sum()
        anomaly_rate = (total_anomalies / total_records * 100) if total_records > 0 else 0
        
        metrics = {
            'total_records': total_records,
            'total_anomalies': int(total_anomalies),
            'anomaly_rate': anomaly_rate,
            'normal_records': total_records - total_anomalies
        }
        
        return metrics
    
    def calculate_energy_savings(self, df):
        """
        Calculate potential energy savings from anomaly detection
        
        Args:
            df (pd.DataFrame): Anomaly data
            
        Returns:
            dict: Energy savings metrics
        """
        # Calculate average power consumption for anomalies
        anomaly_records = df[df['is_anomaly'] == True]
        
        if len(anomaly_records) == 0:
            return {
                'total_anomaly_kwh': 0,
                'potential_savings_kwh': 0,
                'potential_savings_cost': 0
            }
        
        # Average power during anomalies (already in kW)
        avg_anomaly_power = anomaly_records['global_active_power_kw'].mean()
        
        # Assume each anomaly lasts 1 hour on average if not corrected
        hours_per_anomaly = 1
        total_anomaly_kwh = len(anomaly_records) * avg_anomaly_power * hours_per_anomaly
        
        # Assume we can reduce 30% of wasted energy by detecting anomalies
        potential_savings_kwh = total_anomaly_kwh * 0.30
        potential_savings_cost = potential_savings_kwh * self.energy_cost_per_kwh
        
        return {
            'total_anomaly_kwh': total_anomaly_kwh,
            'potential_savings_kwh': potential_savings_kwh,
            'potential_savings_cost': potential_savings_cost,
            'avg_anomaly_power_kw': avg_anomaly_power
        }
    
    def calculate_failure_prevention_value(self, df):
        """
        Calculate value from preventing failures
        
        Args:
            df (pd.DataFrame): Anomaly data
            
        Returns:
            dict: Failure prevention metrics
        """
        total_anomalies = df['is_anomaly'].sum()
        
        # Estimate true anomalies (accounting for false positives)
        estimated_true_anomalies = total_anomalies * (1 - self.false_positive_rate)
        
        # Estimate failures prevented
        failures_prevented = estimated_true_anomalies * self.failure_prevention_rate
        
        # Calculate value
        total_value_prevented = failures_prevented * self.cost_prevented_failure
        
        return {
            'estimated_true_anomalies': estimated_true_anomalies,
            'failures_prevented': failures_prevented,
            'total_value_prevented': total_value_prevented,
            'avg_value_per_anomaly': total_value_prevented / total_anomalies if total_anomalies > 0 else 0
        }
    
    def calculate_false_alarm_cost(self, df):
        """
        Calculate cost of false alarms
        
        Args:
            df (pd.DataFrame): Anomaly data
            
        Returns:
            dict: False alarm cost metrics
        """
        total_anomalies = df['is_anomaly'].sum()
        
        # Estimate false positives
        estimated_false_positives = total_anomalies * self.false_positive_rate
        
        # Calculate cost
        total_false_alarm_cost = estimated_false_positives * self.cost_false_alarm
        
        return {
            'estimated_false_positives': estimated_false_positives,
            'total_false_alarm_cost': total_false_alarm_cost,
            'cost_per_false_alarm': self.cost_false_alarm
        }
    
    def calculate_roi(self, df, system_cost=10000):
        """
        Calculate overall ROI
        
        Args:
            df (pd.DataFrame): Anomaly data
            system_cost (float): Total cost of implementing the system
            
        Returns:
            dict: Complete ROI analysis
        """
        # Get all metrics
        basic_metrics = self.calculate_basic_metrics(df)
        energy_savings = self.calculate_energy_savings(df)
        failure_prevention = self.calculate_failure_prevention_value(df)
        false_alarm_costs = self.calculate_false_alarm_cost(df)
        
        # Calculate total benefits
        total_benefits = (
            energy_savings['potential_savings_cost'] +
            failure_prevention['total_value_prevented']
        )
        
        # Calculate total costs
        total_costs = system_cost + false_alarm_costs['total_false_alarm_cost']
        
        # Calculate ROI
        net_benefit = total_benefits - total_costs
        roi_percentage = (net_benefit / total_costs * 100) if total_costs > 0 else 0
        payback_period_days = (total_costs / (total_benefits / 365)) if total_benefits > 0 else float('inf')
        
        roi_summary = {
            'system_cost': system_cost,
            'total_benefits': total_benefits,
            'total_costs': total_costs,
            'net_benefit': net_benefit,
            'roi_percentage': roi_percentage,
            'payback_period_days': payback_period_days,
            'benefit_cost_ratio': total_benefits / total_costs if total_costs > 0 else 0
        }
        
        # Combine all metrics
        complete_analysis = {
            'basic_metrics': basic_metrics,
            'energy_savings': energy_savings,
            'failure_prevention': failure_prevention,
            'false_alarm_costs': false_alarm_costs,
            'roi_summary': roi_summary
        }
        
        return complete_analysis
    
    def generate_roi_report(self, analysis, output_file='docs/roi_report.txt'):
        """
        Generate a formatted ROI report
        
        Args:
            analysis (dict): ROI analysis results
            output_file (str): Path to save the report
        """
        report_lines = []
        report_lines.append("=" * 70)
        report_lines.append("G4 - ANOMALY DETECTION SYSTEM - ROI ANALYSIS REPORT")
        report_lines.append("=" * 70)
        report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # Basic Metrics
        report_lines.append("1. DETECTION METRICS")
        report_lines.append("-" * 70)
        bm = analysis['basic_metrics']
        report_lines.append(f"Total records analyzed:    {bm['total_records']:,}")
        report_lines.append(f"Anomalies detected:        {bm['total_anomalies']:,}")
        report_lines.append(f"Anomaly rate:              {bm['anomaly_rate']:.2f}%")
        report_lines.append("")
        
        # Energy Savings
        report_lines.append("2. ENERGY SAVINGS")
        report_lines.append("-" * 70)
        es = analysis['energy_savings']
        report_lines.append(f"Total anomaly energy:      {es['total_anomaly_kwh']:.2f} kWh")
        report_lines.append(f"Potential savings:         {es['potential_savings_kwh']:.2f} kWh")
        report_lines.append(f"Energy cost savings:       ${es['potential_savings_cost']:,.2f}")
        report_lines.append("")
        
        # Failure Prevention
        report_lines.append("3. FAILURE PREVENTION VALUE")
        report_lines.append("-" * 70)
        fp = analysis['failure_prevention']
        report_lines.append(f"True anomalies (est.):     {fp['estimated_true_anomalies']:.0f}")
        report_lines.append(f"Failures prevented:        {fp['failures_prevented']:.0f}")
        report_lines.append(f"Value of prevention:       ${fp['total_value_prevented']:,.2f}")
        report_lines.append("")
        
        # False Alarm Costs
        report_lines.append("4. FALSE ALARM COSTS")
        report_lines.append("-" * 70)
        fa = analysis['false_alarm_costs']
        report_lines.append(f"False positives (est.):    {fa['estimated_false_positives']:.0f}")
        report_lines.append(f"Total false alarm cost:    ${fa['total_false_alarm_cost']:,.2f}")
        report_lines.append("")
        
        # ROI Summary
        report_lines.append("5. ROI SUMMARY")
        report_lines.append("=" * 70)
        roi = analysis['roi_summary']
        report_lines.append(f"System implementation cost: ${roi['system_cost']:,.2f}")
        report_lines.append(f"Total benefits:             ${roi['total_benefits']:,.2f}")
        report_lines.append(f"Total costs:                ${roi['total_costs']:,.2f}")
        report_lines.append("")
        report_lines.append(f"NET BENEFIT:                ${roi['net_benefit']:,.2f}")
        report_lines.append(f"ROI:                        {roi['roi_percentage']:.2f}%")
        report_lines.append(f"Benefit-Cost Ratio:         {roi['benefit_cost_ratio']:.2f}")
        
        if roi['payback_period_days'] != float('inf'):
            report_lines.append(f"Payback period:             {roi['payback_period_days']:.0f} days")
        else:
            report_lines.append(f"Payback period:             Not achievable with current data")
        
        report_lines.append("=" * 70)
        
        # Save to file
        report_text = "\n".join(report_lines)
        
        try:
            with open(output_file, 'w') as f:
                f.write(report_text)
            logger.info(f"✓ ROI report saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving report: {e}")
        
        # Also print to console
        print("\n" + report_text)
        
        return report_text


# Main function for standalone execution
if __name__ == "__main__":
    roi_calc = ROICalculator()
    
    if roi_calc.connect():
        # Get data
        df = roi_calc.get_anomaly_data()
        
        if len(df) > 0:
            # Calculate ROI
            analysis = roi_calc.calculate_roi(df, system_cost=10000)
            
            # Generate report
            roi_calc.generate_roi_report(analysis)
        else:
            logger.warning("No data available for ROI analysis")
        
        roi_calc.disconnect()
