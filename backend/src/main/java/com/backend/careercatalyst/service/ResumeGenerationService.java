package com.backend.careercatalyst.service;

import com.backend.careercatalyst.dto.GenerateRequest;
import com.backend.careercatalyst.exception.PythonServiceException;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Service;
import org.springframework.web.reactive.function.client.WebClient;
import reactor.core.publisher.Mono;
import reactor.core.scheduler.Schedulers;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipInputStream;

@Service
public class ResumeGenerationService {

    private final WebClient webClient;
    private final FileStorageService fileStorageService;

    @Autowired
    public ResumeGenerationService(WebClient.Builder webClientBuilder,
                                   FileStorageService fileStorageService,
                                   @Value("${python.service.url}") String pythonServiceUrl) {
        this.webClient = webClientBuilder.baseUrl(pythonServiceUrl).build();
        this.fileStorageService = fileStorageService;
    }

    /**
     * Calls the external Python microservice to generate the resume files.
     *
     * @param generateRequest The request data.
     * @return A Mono emitting the response as a byte array (zipped files).
     */
    private Mono<byte[]> callPythonService(GenerateRequest generateRequest) {
        return this.webClient.post()
            .uri("/generate")
            .bodyValue(generateRequest)
            .retrieve()
            .bodyToMono(byte[].class)
            .onErrorMap(ex -> new PythonServiceException("Failed to get response from Python service", ex));
    }

    /**
     * Generates a resume, saves the files, and returns their download URLs.
     * This method is fully reactive.
     *
     * @param generateRequest The request data.
     * @return A Mono emitting a map of download URLs for the generated files.
     */
    public Mono<Map<String, String>> generateAndSaveResume(GenerateRequest generateRequest) {
        return callPythonService(generateRequest)
            .flatMap(zipFileBytes ->
                // Wrap the blocking file I/O operation and run it on a dedicated thread pool
                Mono.fromCallable(() -> fileStorageService.saveAndUnzipFiles(zipFileBytes))
                    .subscribeOn(Schedulers.boundedElastic())
                    .map(sessionId -> Map.of(
                        "pdfUrl", "/api/v1/download/" + sessionId + "/resume.pdf",
                        "latexUrl", "/api/v1/download/" + sessionId + "/resume.tex",
                        "jsonUrl", "/api/v1/download/" + sessionId + "/resume.json"
                    ))
            );
    }

    /**
     * Generates a resume and returns the PDF content directly for previewing.
     *
     * @param generateRequest The request data.
     * @return A Mono emitting the raw byte array of the generated PDF.
     */
    public Mono<byte[]> getResumePreview(GenerateRequest generateRequest) {
        return callPythonService(generateRequest)
            .map(zipFileBytes -> {
                try {
                    return unzipFileFromBytes(zipFileBytes, "resume.pdf");
                } catch (IOException e) {
                    // Wrap the checked exception in a custom unchecked exception
                    throw new PythonServiceException("Failed to extract PDF from preview response.", e);
                }
            });
    }

    /**
     * Loads a file from storage to be served for download.
     *
     * @param sessionId The unique ID of the generation session.
     * @param fileName  The name of the file to load.
     * @return The file as a Spring Resource.
     */
    public Resource loadFileAsResource(String sessionId, String fileName) {
        return fileStorageService.loadFileAsResource(sessionId, fileName);
    }

    /**
     * Helper method to extract a single file from a zipped byte array.
     *
     * @param zipBytes          The byte array of the zip archive.
     * @param fileNameToExtract The name of the file to find and extract.
     * @return The byte array of the extracted file.
     * @throws IOException if the file is not found or an I/O error occurs.
     */
    private byte[] unzipFileFromBytes(byte[] zipBytes, String fileNameToExtract) throws IOException {
        try (ZipInputStream zis = new ZipInputStream(new ByteArrayInputStream(zipBytes))) {
            ZipEntry zipEntry;
            while ((zipEntry = zis.getNextEntry()) != null) {
                if (fileNameToExtract.equals(zipEntry.getName())) {
                    return zis.readAllBytes();
                }
            }
        }
        throw new IOException("File not found in zip archive: " + fileNameToExtract);
    }
}