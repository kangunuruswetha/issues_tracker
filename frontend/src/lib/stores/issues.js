import { writable } from 'svelte/store';

export const issues = writable([]);
export const dashboardStats = writable({
    total_issues: 0,
    open_issues: 0,
    severity_breakdown: {},
    status_breakdown: {}
});

// WebSocket connection store
export const wsConnection = writable(null);

export function addIssue(issue) {
    issues.update(current => [...current, issue]);
}

export function updateIssue(updatedIssue) {
    issues.update(current => 
        current.map(issue => 
            issue.id === updatedIssue.id ? updatedIssue : issue
        )
    );
}

export function removeIssue(issueId) {
    issues.update(current => 
        current.filter(issue => issue.id !== issueId)
    );
}

export function setIssues(newIssues) {
    issues.set(newIssues);
}

export function updateDashboardStats(stats) {
    dashboardStats.set(stats);
}
