function deleteFeedback(feedbackId) {
    fetch("/delete-feedback", {
        method: "POST",
        body: JSON.stringify({ feedbackId: feedbackId }),
    }).then((_res) => {
        window.location.href = "/feedback";
    });
}