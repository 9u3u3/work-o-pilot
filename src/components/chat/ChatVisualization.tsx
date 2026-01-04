import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar, ResponsiveContainer } from "recharts";
import { Message } from "@/types/chat";

interface ChatVisualizationProps {
    visualization: NonNullable<Message["visualization"]>;
}

const COLORS = ["#8884d8", "#82ca9d", "#ffc658", "#ff7300", "#0088FE", "#00C49F", "#FFBB28", "#FF8042"];

export function ChatVisualization({ visualization }: ChatVisualizationProps) {
    const { type, chart_data, image_base64 } = visualization;

    if (image_base64) {
        return (
            <div className="w-full mt-4">
                <img
                    src={`data:image/png;base64,${image_base64}`}
                    alt="Analytics Visualization"
                    className="max-w-full h-auto rounded-lg border border-border"
                />
            </div>
        );
    }

    if (!chart_data || type === "none") return null;

    const containerClass = "w-full h-64 mt-4";

    switch (type) {
        case "pie_chart": {
            const data = chart_data.labels?.map((label, i) => ({
                name: label,
                value: chart_data.values?.[i] || 0,
            })) || [];

            return (
                <div className={containerClass}>
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={data}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                                outerRadius={80}
                                fill="#8884d8"
                                dataKey="value"
                            >
                                {data.map((_, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip />
                            <Legend />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            );
        }

        case "line_chart": {
            const datasets = chart_data.datasets || [];
            // Transform data for Recharts
            const allDates = new Set<string>();
            datasets.forEach((ds) => ds.data.forEach((d) => allDates.add(d.x)));
            const sortedDates = Array.from(allDates).sort();

            const data = sortedDates.map((date) => {
                const point: Record<string, unknown> = { date };
                datasets.forEach((ds) => {
                    const found = ds.data.find((d) => d.x === date);
                    point[ds.label] = found?.y || null;
                });
                return point;
            });

            return (
                <div className={containerClass}>
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={data}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="date" />
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            {datasets.map((ds, i) => (
                                <Line key={ds.label} type="monotone" dataKey={ds.label} stroke={COLORS[i % COLORS.length]} />
                            ))}
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            );
        }

        case "bar_chart": {
            const data = chart_data.labels?.map((label, i) => ({
                name: label,
                value: chart_data.values?.[i] || 0,
            })) || [];

            return (
                <div className={containerClass}>
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={data}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="value" fill="#8884d8">
                                {data.map((_, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Bar>
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            );
        }

        case "table": {
            const tableData = chart_data.data || [];
            if (tableData.length === 0) return null;
            const headers = Object.keys(tableData[0]);

            return (
                <div className="mt-4 overflow-x-auto">
                    <table className="w-full border-collapse border border-border text-sm">
                        <thead>
                            <tr className="bg-muted">
                                {headers.map((h) => (
                                    <th key={h} className="border border-border px-3 py-2 text-left font-medium">
                                        {h}
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {tableData.map((row, i) => (
                                <tr key={i} className="hover:bg-muted/50">
                                    {headers.map((h) => (
                                        <td key={h} className="border border-border px-3 py-2">
                                            {String(row[h] ?? "")}
                                        </td>
                                    ))}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            );
        }

        default:
            return null;
    }
}
