import AirQualityDashboard from "./components/air-quality-dashboard";
import InfocreonHeader from "./components/infocreon-header";

export default function Home() {
return ( <div className="relative min-h-screen"> <InfocreonHeader /> <AirQualityDashboard /> </div>
);
}
