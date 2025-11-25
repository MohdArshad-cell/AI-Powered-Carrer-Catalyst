package com.backend.careercatalyst.controller;

import com.backend.careercatalyst.dto.CoverLetterRequest; // <-- NEW
import com.backend.careercatalyst.dto.CoverLetterResponse; // <-- NEW
import com.backend.careercatalyst.dto.EvaluationRequest;
import com.backend.careercatalyst.dto.EvaluationResponse;
import com.backend.careercatalyst.dto.GenerateRequest;
import com.backend.careercatalyst.dto.InterviewResponse;
import com.backend.careercatalyst.dto.TailorRequest; // <-- NEW
import com.backend.careercatalyst.dto.TailorResponse; // <-- NEW
import com.backend.careercatalyst.service.AiService; // <-- NEW
import com.backend.careercatalyst.service.ResumeGenerationService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.core.io.Resource;
import org.springframework.http.ContentDisposition;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers; // <-- NEW
import com.backend.careercatalyst.dto.InterviewResponse;
import java.util.Map;

@RestController
@RequestMapping("/api/v1")
public class ApiController {

    private final ResumeGenerationService resumeGenerationService;
    private final AiService aiService; // <-- NEW: Inject the AiService

    @Autowired
    public ApiController(ResumeGenerationService resumeGenerationService, AiService aiService) {
        this.resumeGenerationService = resumeGenerationService;
        this.aiService = aiService;
    }

    /**
     * Endpoint to generate a new resume.
     */
    @PostMapping("/generate")
    public Mono<ResponseEntity<Map<String, String>>> generateResume(@RequestBody GenerateRequest generateRequest) {
        return resumeGenerationService.generateAndSaveResume(generateRequest)
                .map(response -> ResponseEntity.ok(response))
                .onErrorResume(e -> {
                    e.printStackTrace();
                    return Mono.just(ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build());
                });
    }

    /**
     * Endpoint to get a PDF preview of the resume.
     */
    @PostMapping("/preview")
    public Mono<ResponseEntity<byte[]>> previewResume(@RequestBody GenerateRequest generateRequest) {
        return resumeGenerationService.getResumePreview(generateRequest)
                .map(pdfBytes -> {
                    HttpHeaders headers = new HttpHeaders();
                    headers.setContentType(MediaType.APPLICATION_PDF);
                    headers.setContentDisposition(ContentDisposition.inline().filename("resume_preview.pdf").build());
                    return new ResponseEntity<>(pdfBytes, headers, HttpStatus.OK);
                })
                .onErrorResume(e -> {
                    e.printStackTrace();
                    return Mono.just(ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build());
                });
    }

    // --- NEW AI TAILOR ENDPOINT ---
    /**
     * Endpoint to tailor a resume using an AI model.
     * @param request The request body containing the resume and job description text.
     * @return A ResponseEntity with the AI-generated suggestions.
     */
    @PostMapping("/tailor")
    public Mono<ResponseEntity<TailorResponse>> tailorResume(@RequestBody TailorRequest request) {
        // Since running a Python script is a blocking operation, we wrap it
        // and run it on a dedicated thread pool to keep the controller non-blocking.
        return Mono.fromCallable(() -> aiService.getTailoredResume(request.getResumeText(), request.getJobDescription()))
                .subscribeOn(Schedulers.boundedElastic())
                .map(tailoredContent -> ResponseEntity.ok(new TailorResponse(tailoredContent)))
                .onErrorResume(e -> {
                    e.printStackTrace();
                    TailorResponse errorResponse = new TailorResponse("Error: " + e.getMessage());
                    return Mono.just(ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse));
                });
    }
    // ---------------------------------
    // --- NEW: AI ATS EVALUATOR ENDPOINT ---
    /**
     * Endpoint to evaluate a resume against a job description.
     * @param request The request body containing the resume and job description.
     * @return A ResponseEntity with the AI-generated evaluation.
     */
    @PostMapping("/evaluate-resume")
    public Mono<ResponseEntity<EvaluationResponse>> evaluateResume(@RequestBody EvaluationRequest request) {
        // Wrap the blocking script call in a non-blocking Mono
        return Mono.fromCallable(() -> aiService.getEvaluationResult(request.getResume(), request.getJobDescription()))
                .subscribeOn(Schedulers.boundedElastic())
                .map(evaluationContent -> ResponseEntity.ok(new EvaluationResponse(evaluationContent)))
                .onErrorResume(e -> {
                    e.printStackTrace();
                    EvaluationResponse errorResponse = new EvaluationResponse("Error: " + e.getMessage());
                    return Mono.just(ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse));
                });
    }

    // --- NEW: AI COVER LETTER GENERATOR ENDPOINT ---
    /**
     * Endpoint to generate a cover letter based on a resume and job description.
     * @param request The request body containing the resume and job description.
     * @return A ResponseEntity with the AI-generated cover letter.
     */
    @PostMapping("/generate-cover-letter")
    public Mono<ResponseEntity<CoverLetterResponse>> generateCoverLetter(@RequestBody CoverLetterRequest request) {
        // Wrap the blocking script call in a non-blocking Mono
        return Mono.fromCallable(() -> aiService.getGeneratedCoverLetter(request.getResume(), request.getJobDescription()))
                .subscribeOn(Schedulers.boundedElastic())
                .map(coverLetterContent -> ResponseEntity.ok(new CoverLetterResponse(coverLetterContent)))
                .onErrorResume(e -> {
                    e.printStackTrace();
                    CoverLetterResponse errorResponse = new CoverLetterResponse("Error: " + e.getMessage());
                    return Mono.just(ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).body(errorResponse));
                });
    }

    // --- NEW: AI MOCK INTERVIEW ENDPOINT ---
    @PostMapping("/interview/generate")
    public Mono<ResponseEntity<InterviewResponse>> generateInterviewQuestions(@RequestBody String jobDescription) {
        return Mono.fromCallable(() -> aiService.getInterviewQuestions(jobDescription))
                .subscribeOn(Schedulers.boundedElastic())
                .map(jsonContent -> ResponseEntity.ok(new InterviewResponse(jsonContent)))
                .onErrorResume(e -> {
                    e.printStackTrace();
                    return Mono.just(ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR)
                        .body(new InterviewResponse("{\"error\": \"" + e.getMessage() + "\"}")));
                });
    }
    /**
     * Endpoint to download a previously generated file (PDF, TeX, or JSON).
     */
    @GetMapping("/download/{sessionId}/{fileName:.+}")
    public ResponseEntity<Resource> downloadFile(@PathVariable String sessionId, @PathVariable String fileName) {
        try {
            Resource resource = resumeGenerationService.loadFileAsResource(sessionId, fileName);
            String contentType = "application/octet-stream";

            if (fileName.endsWith(".pdf")) {
                contentType = "application/pdf";
            } else if (fileName.endsWith(".tex")) {
                contentType = "application/x-tex";
            } else if (fileName.endsWith(".json")) {
                contentType = "application/json";
            }

            return ResponseEntity.ok()
                    .contentType(MediaType.parseMediaType(contentType))
                    .header(HttpHeaders.CONTENT_DISPOSITION, "attachment; filename=\"" + resource.getFilename() + "\"")
                    .body(resource);
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.NOT_FOUND).build();
        }
    }
}