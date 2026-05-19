package com.danieloliveira.api_grpc.service;

import com.danieloliveira.api_grpc.model.Product;
import com.danieloliveira.api_grpc.repository.ProductRepository;
import com.danieloliveira.grpc.ProductGrpcServiceGrpc;
import com.danieloliveira.grpc.ProductRequest;
import com.danieloliveira.grpc.ProductResponse;
import com.google.protobuf.Empty;
import io.grpc.stub.StreamObserver;
import lombok.RequiredArgsConstructor;
import net.devh.boot.grpc.server.service.GrpcService;

import java.time.LocalDateTime;

@GrpcService
@RequiredArgsConstructor
public class ProductService extends ProductGrpcServiceGrpc.ProductGrpcServiceImplBase {

    private final ProductRepository productRepository;

    private static void setProductsAttributes(Product existingProduct, ProductRequest request) {
        existingProduct.setName(request.getName());
        existingProduct.setDescription(request.getDescription());
        existingProduct.setPrice(request.getPrice());
        existingProduct.setStock(request.getStock());
        existingProduct.setCategory(request.getCategory());
    }

    @Override
    public void create(com.danieloliveira.grpc.ProductRequest request, StreamObserver<com.danieloliveira.grpc.ProductResponse> responseObserver) {
        // 1. Simula a criação da Entidade (como se fosse para o banco)
        Product product = toProduct(request);

        // 2. Salva no "Banco" (Map)
        productRepository.save(product);

        // 3. Converte para o formato gRPC e envia
        responseObserver.onNext(mapToProto(product));
        responseObserver.onCompleted();
    }

    @Override
    public void findById(com.danieloliveira.grpc.GetProductRequest request, StreamObserver<com.danieloliveira.grpc.ProductResponse> responseObserver) {
        responseObserver.onNext(mapToProto(productRepository.findById(request.getId())));
        responseObserver.onCompleted();
    }

    @Override
    public void update(com.danieloliveira.grpc.UpdateProductRequest request, StreamObserver<com.danieloliveira.grpc.ProductResponse> responseObserver) {
        long id = request.getId();

        // 2. Busca o produto existente no "banco"
        Product existingProduct = productRepository.findById(id);


        // 3. Atualiza os dados da nossa Entidade de Domínio
        setProductsAttributes(existingProduct, request.getProduct());
        // createdAt geralmente não muda no update

        // 4. Salva (No Map o put substitui se a chave for a mesma)
        productRepository.save(existingProduct);

        // 5. Converte para gRPC e envia a resposta de sucesso
        responseObserver.onNext(mapToProto(existingProduct));

        responseObserver.onCompleted();
    }

    @Override
    public void delete(com.danieloliveira.grpc.GetProductRequest request, StreamObserver<Empty> responseObserver) {
        productRepository.delete(request.getId());
        responseObserver.onNext(Empty.getDefaultInstance());
        responseObserver.onCompleted();
    }

    /// /////////////////////////////////////////////////////////////////////////////////////////////////////////////////

    private Product toProduct(ProductRequest request) {
        Product product = new Product();
        product.setId(productRepository.incrementSequence());
        setProductsAttributes(product, request);
        product.setCreatedAt(LocalDateTime.now());
        return product;
    }

    private ProductResponse mapToProto(Product product) {
        return ProductResponse.newBuilder()
                .setId(product.getId())
                .setName(product.getName())
                .setDescription(product.getDescription())
                .setPrice(product.getPrice())
                .setStock(product.getStock())
                .setCategory(product.getCategory())
                .setCreatedAt(product.getCreatedAt().toString())
                .build();
    }
}
